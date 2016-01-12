#!/usr/bin/env python3
"""Tests live plotting of signal filtering using actors."""
# Python imports
import sys
import time
import logging
from collections import deque

# Dependency imports
import numpy as np
import pykka
import pyqtgraph as pg

# Package imports
from .. import actors, leg, signal

logging.basicConfig(level=logging.INFO)

class Filterer(actors.Broadcaster, pykka.ThreadingActor):
    """Filters samples of a signal."""
    def __init__(self, filter_width=None, filterer=np.median):
        super().__init__()
        self.filterer = signal.moving_filter(filter_width, filterer)

    def on_receive(self, message):
        filtered = self.filterer.send((message['time'], message['fluid pressure']))
        if filtered is not None:
            self.broadcast({'time': filtered[0], 'data': 'fluid pressure',
                            'fluid pressure': filtered[1]}, 'fluid pressure')

class CurveUpdater(pykka.ThreadingActor):
    """Updates a PyQtGraph curve with samples."""
    def __init__(self, curve, max_samples=None):
        super().__init__()
        self.curve = curve
        self.curve_x = deque(maxlen=max_samples)
        self.curve_y = deque(maxlen=max_samples)

    def on_receive(self, message):
        """Slot that updates the curves with the next sample."""
        sample_time = message['time']
        sample = message['fluid pressure']
        self.curve_x.append(sample_time)
        self.curve_y.append(sample)
        self.curve.setData(self.curve_x, self.curve_y)

def stream(update_interval, filter_width, max_samples):
    """Continuously generates noisy data and filters it and plots it live."""
    # Plotting
    graph = pg.plot()
    graph.addLegend()
    signal_curve = graph.plot(pen='r', name="Raw (Noisy) Signal")
    filtered_curve = graph.plot(pen='b', name="Median Filtered Signal")

    signal_curve_updater = CurveUpdater.start(signal_curve, max_samples)

    filtered_curve_updater = CurveUpdater.start(filtered_curve, max_samples)
    signal_filter = Filterer.start(filter_width=filter_width)
    signal_filter.proxy().register(filtered_curve_updater, 'fluid pressure')

    leg_monitor = leg.LegMonitor().start()
    leg_monitor.proxy().register(signal_curve_updater, 'fluid pressure')
    leg_monitor.proxy().register(signal_filter, 'fluid pressure')
    leg_monitor.tell({'command': 'start producing', 'interval': update_interval})

if __name__ == "__main__":
    pg.setConfigOptions(antialias=True, background='w', foreground='k')
    stream(0.05, 40, 100)
    pg.Qt.QtGui.QApplication.instance().exec_()
    pykka.ActorRegistry.stop_all() # stop actors in LIFO order
    sys.exit()
