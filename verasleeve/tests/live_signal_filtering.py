#!/usr/bin/env python3
"""Tests live plotting of signal filtering using actors."""
# Python imports
import sys
import time
import logging

# Dependency imports
import numpy as np
import pykka
import pyqtgraph as pg

# Package imports
from .. import signal
from .. import actors
from . import signal_filtering

logging.basicConfig(level=logging.INFO)

class SignalGenerator(actors.Broadcaster, actors.Producer):
    """Generates samples of a signal."""
    def __init__(self, signal_function, signal_length):
        super().__init__()
        self.signal_function = signal_function(signal_length)

    def _on_produce(self):
        try:
            (sample_number, sample) = next(self.signal_function)
            self.broadcast({'sample number': sample_number, 'sample': sample}, 'signal')
        except StopIteration:
            logging.info("Finished generating signal.")
            self.actor_ref.tell({'command': 'stop producing'})

class Filterer(actors.Broadcaster, pykka.ThreadingActor):
    """Filters samples of a signal."""
    def __init__(self, filter_width=None, filterer=np.median):
        super().__init__()
        self.filterer = signal.moving_filter(filter_width, filterer)

    def on_receive(self, message):
        filtered = self.filterer.send((message['sample number'], message['sample']))
        if filtered is not None:
            self.broadcast({'sample number': filtered[0], 'sample': filtered[1]}, 'filtered')

class CurveUpdater(pykka.ThreadingActor):
    """Updates a PyQtGraph curve with samples."""
    def __init__(self, curve):
        super().__init__()
        self.curve = curve
        self.curve_x = []
        self.curve_y = []

    def on_receive(self, message):
        """Slot that updates the curves with the next sample."""
        sample_number = message['sample number']
        sample = message['sample']
        self.curve_x.append(sample_number)
        self.curve_y.append(sample)
        self.curve.setData(self.curve_x, self.curve_y)

def stream(signal_generator):
    """Continuously generates noisy data and filters it and plots it live."""
    # Plotting
    graph = pg.plot()
    graph.addLegend()
    signal_curve = graph.plot(pen='r', name="Raw (Noisy) Signal")
    filtered_curve = graph.plot(pen='b', name="Median Filtered Signal")
    average_curve = graph.plot(pen='k', name="Moving Average of Signal")

    signal_curve_updater = CurveUpdater.start(signal_curve)
    signal_generator = SignalGenerator.start(signal_generator, 500)
    signal_generator.proxy().register(signal_curve_updater, 'signal')

    filtered_curve_updater = CurveUpdater.start(filtered_curve)
    signal_filter = Filterer.start(filter_width=10)
    signal_generator.proxy().register(signal_filter, 'signal')
    signal_filter.proxy().register(filtered_curve_updater, 'filtered')

    average_curve_updater = CurveUpdater.start(average_curve)
    signal_average = Filterer.start(filterer=np.mean)
    signal_generator.proxy().register(signal_average, 'signal')
    signal_average.proxy().register(average_curve_updater, 'filtered')

    signal_generator.tell({'command': 'start producing', 'interval': 0.05})

if __name__ == "__main__":
    pg.setConfigOptions(antialias=True, background='w', foreground='k')
    stream(signal_filtering.square_wave)
    pg.Qt.QtGui.QApplication.instance().exec_()
    pykka.ActorRegistry.stop_all() # stop actors in LIFO order
    sys.exit()
