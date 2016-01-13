#!/usr/bin/env python3
"""Tests live plotting of signal filtering using actors."""
# Python imports
import sys
import logging

# Dependency imports
import pykka
import pyqtgraph as pg

# Package imports
from .. import leg, signal, plotting

logging.basicConfig(level=logging.INFO)

def stream(update_interval, filter_width, max_samples):
    """Continuously generates noisy data and filters it and plots it live."""
    # Plotting
    graph = pg.plot()
    graph.addLegend()
    signal_curve = graph.plot(pen='r', name="Raw (Noisy) Signal")
    filtered_curve = graph.plot(pen='b', name="Median Filtered Signal")

    signal_curve_updater = plotting.CurveUpdater.start(signal_curve, max_samples)

    filtered_curve_updater = plotting.CurveUpdater.start(filtered_curve, max_samples)
    signal_filter = signal.Filterer.start(filter_width=filter_width)
    signal_filter.proxy().register(filtered_curve_updater, 'fluid pressure')

    try:
        leg_monitor = leg.LegMonitor().start()
    except RuntimeError:
        pykka.ActorRegistry.stop_all() # stop actors in LIFO order
        raise
    leg_monitor.proxy().register(signal_curve_updater, 'fluid pressure')
    leg_monitor.proxy().register(signal_filter, 'fluid pressure')
    leg_monitor.tell({'command': 'start producing', 'interval': update_interval})

if __name__ == "__main__":
    pg.setConfigOptions(antialias=True, background='w', foreground='k')
    stream(0.05, 40, 100)
    pg.Qt.QtGui.QApplication.instance().exec_()
    pykka.ActorRegistry.stop_all() # stop actors in LIFO order
    sys.exit()
