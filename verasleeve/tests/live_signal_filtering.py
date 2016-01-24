#!/usr/bin/env python3
"""Tests live plotting of signal filtering using actors."""
# Python imports
import sys
import logging

# Dependency imports
import numpy as np
import pykka
import pyqtgraph as pg

# Package imports
from .. import actors, signal, plotting
from . import signal_filtering

logging.basicConfig(level=logging.INFO)

class SignalGenerator(actors.Broadcaster, actors.Producer):
    """Generates samples of a signal."""
    def __init__(self, signal_function, signal_length):
        super().__init__()
        self.signal_function = signal_function(signal_length)

    def _on_produce(self):
        try:
            (time, sample) = next(self.signal_function)
            self.broadcast({'time': time, 'type': 'signal', 'data': sample}, 'signal')
        except StopIteration:
            logging.info("Finished generating signal.")
            self.actor_ref.tell({'command': 'stop producing'})

def stream(signal_generator):
    """Continuously generates noisy data and filters it and plots it live."""
    # Plotting
    graph = pg.plot()
    graph.addLegend()
    signal_curve = graph.plot(pen='r', name="Raw (Noisy) Signal")
    filtered_curve = graph.plot(pen='b', name="Median Filtered Signal")
    average_curve = graph.plot(pen='k', name="Moving Average of Signal")

    signal_curve_updater = plotting.CurveUpdater.start(signal_curve)
    signal_generator = SignalGenerator.start(signal_generator, 500)
    signal_generator.proxy().register(signal_curve_updater, 'signal')

    filtered_curve_updater = plotting.CurveUpdater.start(filtered_curve)
    signal_filter = signal.Filterer.start(filter_width=10)
    signal_generator.proxy().register(signal_filter, 'signal')
    signal_filter.proxy().register(filtered_curve_updater, 'signal')

    average_curve_updater = plotting.CurveUpdater.start(average_curve)
    signal_average = signal.Filterer.start(filterer=np.mean)
    signal_generator.proxy().register(signal_average, 'signal')
    signal_average.proxy().register(average_curve_updater, 'signal')

    signal_generator.tell({'command': 'start producing', 'interval': 0.05})

if __name__ == "__main__":
    pg.setConfigOptions(antialias=True, background='w', foreground='k')
    stream(signal_filtering.square_wave)
    pg.Qt.QtGui.QApplication.instance().exec_()
    pykka.ActorRegistry.stop_all() # stop actors in LIFO order
    sys.exit()
