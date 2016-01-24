#!/usr/bin/env python3
"""Monitors the fluid pressure sensor reading."""
# Python imports
import sys
import os

# Dependency imports
import pykka
import pyqtgraph as pg
from pyqtgraph.Qt import uic, QtGui

# Package imports
from verasleeve import leg, signal, plotting, gui

_UI_LAYOUT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'leg_monitor.ui')

class LegMonitorPanel(QtGui.QMainWindow):
    def __init__(self, update_interval, filter_width, max_samples):
        super().__init__()
        self.__ui = uic.loadUi(_UI_LAYOUT_PATH)
        self.__ui.show()
        self.__init_window()
        self.__init_graphs()
        self.__init_labels()
        self.__init_updaters(max_samples)
        self.__init_filters(filter_width)
        self.__init_monitoring(update_interval)

    def __init_window(self):
        # Actions
        self.__ui.actionExit.triggered.connect(QtGui.QApplication.instance().quit)

    def __init_graphs(self):
        self.__graphs = {
            'fluid pressure': self.__ui.fluidPlot.getPlotItem(),
            'surface pressure 0': self.__ui.sensor0Plot.getPlotItem(),
            'surface pressure 1': self.__ui.sensor1Plot.getPlotItem(),
            'surface pressure 2': self.__ui.sensor2Plot.getPlotItem(),
            'surface pressure 3': self.__ui.sensor3Plot.getPlotItem()
        }
        for (_, graph) in self.__graphs.items():
            graph.disableAutoRange(axis=pg.ViewBox.YAxis)
            graph.setLabels(bottom="Time (s)", left="Pin Value (0-1024)")
            graph.addLegend()
        self.__graphs['fluid pressure'].getViewBox().setYRange(50, 400)
        self.__graphs['fluid pressure'].setTitle("Fluid Pressure Sensor Reading")
        for sensor_id in leg.SURFACE_SENSOR_IDS:
            graph = self.__graphs['surface pressure {}'.format(sensor_id)]
            graph.getViewBox().setYRange(0, 1024)

    def __init_labels(self):
        self.__labels = {
            'fluid pressure': self.__ui.fluidValue,
            'surface pressure 0': self.__ui.sensor0Value,
            'surface pressure 1': self.__ui.sensor1Value,
            'surface pressure 2': self.__ui.sensor2Value,
            'surface pressure 3': self.__ui.sensor3Value
        }

    def __init_updaters(self, max_samples):
        self.__raw_curve_updaters = {}
        self.__filtered_curve_updaters = {}
        self.__filtered_label_updaters = {}
        for (graph_name, graph) in self.__graphs.items():
            raw_curve = graph.plot(pen='r', name="raw")
            raw_curve_updater = plotting.CurveUpdater.start(raw_curve, max_samples)
            self.__raw_curve_updaters[graph_name] = raw_curve_updater
            filtered_curve = graph.plot(pen='b', name="filtered")
            filtered_curve_updater = plotting.CurveUpdater.start(filtered_curve, max_samples)
            self.__filtered_curve_updaters[graph_name] = filtered_curve_updater
            filtered_label_updater = gui.LabelUpdater.start(self.__labels[graph_name])
            self.__filtered_label_updaters[graph_name] = filtered_label_updater

    def __init_filters(self, filter_width):
        self.__filterers = {}
        for graph_name in self.__graphs.keys():
            filterer = signal.Filterer.start(filter_width)
            self.__filterers[graph_name] = filterer
            filterer.proxy().register(self.__filtered_curve_updaters[graph_name], graph_name)
            filterer.proxy().register(self.__filtered_label_updaters[graph_name], graph_name)

    def __init_monitoring(self, update_interval):
        try:
            monitor = leg.LegMonitor().start()
        except RuntimeError:
            pykka.ActorRegistry.stop_all() # stop actors in LIFO order
            raise
        for graph_name in self.__graphs.keys():
            monitor.proxy().register(self.__raw_curve_updaters[graph_name], graph_name)
            monitor.proxy().register(self.__filterers[graph_name], graph_name)
        monitor.tell({'command': 'start producing', 'interval': update_interval})

if __name__ == "__main__":
    pg.setConfigOptions(antialias=True, background='w', foreground='k')
    app = QtGui.QApplication(sys.argv)
    leg_monitor_panel = LegMonitorPanel(0.05, 40, 100)
    app.exec_()
    pykka.ActorRegistry.stop_all() # stop actors in LIFO order
    sys.exit()
