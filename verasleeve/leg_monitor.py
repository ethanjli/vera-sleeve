#!/usr/bin/env python3
"""Monitors the fluid pressure sensor reading."""
# Python imports
import sys
import os
import logging

# Dependency imports
import pykka
import pyqtgraph as pg
from pyqtgraph.Qt import uic, QtGui

# Package imports
from verasleeve import leg, signal, plotting, gui

logging.basicConfig(level=logging.INFO)

_UI_LAYOUT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'leg_monitor.ui')

FLUID_PRESSURE_MIN = 0
FLUID_PRESSURE_MAX = 25

class LegMonitorPanel(QtGui.QMainWindow):
    def __init__(self, update_interval, filter_width, graph_width):
        super().__init__()
        self.update_interval = update_interval
        self.__ui = uic.loadUi(_UI_LAYOUT_PATH)
        self.__ui.show()
        self.__init_window()

        self._sensors = {'fluid pressure'}

        self.__init_graphs()
        self.__init_curve_updaters(graph_width)

        self.__init_labels()
        self.__init_label_updaters()

        self.__init_filters(filter_width, graph_width)

        self.__monitor = None
        self.__unit_converter = None

    def __init_window(self):
        # Actions
        self.__ui.actionExit.triggered.connect(QtGui.QApplication.instance().quit)
        self.__ui.actionConnect.triggered.connect(self.__init_monitoring)
        self.__ui.actionStartMonitoring.setDisabled(True)
        self.__ui.actionStartMonitoring.triggered.connect(self.__start_monitoring)
        self.__ui.actionStopMonitoring.setDisabled(True)
        self.__ui.actionStopMonitoring.triggered.connect(self.__stop_monitoring)

    def __init_graphs(self):
        self.__graphs = {
            'fluid pressure': self.__ui.fluidPlot.getPlotItem(),
        }
        for (_, graph) in self.__graphs.items():
            graph.disableAutoRange(axis=pg.ViewBox.YAxis)
            graph.setLabels(bottom="Time (s)", left="Pin Value (0-1024)")
            graph.addLegend()
        self.__graphs['fluid pressure'].getViewBox().setYRange(FLUID_PRESSURE_MIN,
                                                               FLUID_PRESSURE_MAX)
        self.__graphs['fluid pressure'].setTitle("Fluid Pressure, Top of Vein")
        self.__graphs['fluid pressure'].setLabels(left="Pressure (mmHg)")

    def __init_labels(self):
        self.__denoised_labels = {
            'fluid pressure': self.__ui.fluidValue
        }
        self.__max_labels = {
            'fluid pressure': self.__ui.fluidMax
        }
        self.__min_labels = {
            'fluid pressure': self.__ui.fluidMin
        }

    def __init_curve_updaters(self, graph_width):
        curve_types = {
            'raw': {
                'pen': 'r',
                'name': 'Raw'
            },
            'denoised': {
                'pen': 'k',
                'name': 'Denoised'
            },
            'max': {
                'pen': 'g',
                'name': 'Denoised Max'
            },
            'min': {
                'pen': 'b',
                'name': 'Denoised Min'
            }
        }
        self.__curve_updaters = {
            'raw': {},
            'denoised': {},
            'max': {},
            'min': {}
        }
        for name in self._sensors:
            for (curve_type, curve_props) in curve_types.items():
                curve = self.__graphs[name].plot(pen=curve_props['pen'], name=curve_props['name'])
                curve_updater = plotting.CurveUpdater.start(curve, graph_width)
                self.__curve_updaters[curve_type][name] = curve_updater

    def __init_label_updaters(self):
        self.__label_updaters = {
            'denoised': {},
            'max': {},
            'min': {}
        }
        for name in self._sensors:
            denoised_label_updater = gui.LabelUpdater.start(self.__denoised_labels[name],
                                                            "Value")
            self.__label_updaters['denoised'][name] = denoised_label_updater
            max_label_updater = gui.LabelUpdater.start(self.__max_labels[name], "Max")
            self.__label_updaters['max'][name] = max_label_updater
            min_label_updater = gui.LabelUpdater.start(self.__min_labels[name], "Min")
            self.__label_updaters['min'][name] = min_label_updater

    def __init_filters(self, filter_width, graph_width):
        self.__filterers = {
            'denoised': {},
            'max': {},
            'min': {}
        }
        self.__maximizers = {}
        self.__minimizers = {}
        for name in self._sensors:
            filterer = signal.Filterer.start(filter_width)
            self.__filterers['denoised'][name] = filterer
            maximizer = signal.Filterer.start(graph_width // 4, max, "right")
            self.__filterers['max'][name] = maximizer
            filterer.proxy().register(maximizer, name)
            minimizer = signal.Filterer.start(graph_width // 4, min, "right")
            self.__filterers['min'][name] = minimizer
            filterer.proxy().register(minimizer, name)

    def __init_monitoring(self):
        self.__unit_converter = leg.LegUnitConverter.start()
        try:
            self.__monitor = leg.LegMonitor.start()
        except RuntimeError:
            pykka.ActorRegistry.stop_all() # stop actors in LIFO order
            raise
        for name in self._sensors:
            self.__monitor.proxy().register(self.__unit_converter, name)
            self.__unit_converter.proxy().register(self.__filterers['denoised'][name], name)
        self.__ui.actionConnect.setDisabled(True)
        self.__ui.actionStartMonitoring.setDisabled(False)
        self.__ui.actionStartMonitoring.trigger()

    def __start_monitoring(self):
        for name in self._sensors:
            raw_curve_updater = self.__curve_updaters['raw'][name]
            raw_curve_updater.tell({'command': 'clear'})
            self.__unit_converter.proxy().register(raw_curve_updater, name)
            for filter_type in self.__filterers.keys():
                filterer = self.__filterers[filter_type][name]
                filterer.tell({'command': 'clear'})
                curve_updater = self.__curve_updaters[filter_type][name]
                curve_updater.tell({'command': 'clear'})
                filterer.proxy().register(curve_updater, name)
                filterer.proxy().register(self.__label_updaters[filter_type][name], name)
        self.__monitor.tell({'command': 'start producing', 'interval': self.update_interval})
        self.__ui.actionStartMonitoring.setDisabled(True)
        self.__ui.actionStopMonitoring.setDisabled(False)

    def __stop_monitoring(self):
        self.__monitor.tell({'command': 'stop producing'})
        self.__ui.actionStartMonitoring.setDisabled(False)
        self.__ui.actionStopMonitoring.setDisabled(True)
        for name in self._sensors:
            raw_curve_updater = self.__curve_updaters['raw'][name]
            self.__unit_converter.proxy().deregister(raw_curve_updater, name)
            for filter_type in self.__filterers.keys():
                filterer = self.__filterers[filter_type][name]
                filterer.proxy().deregister(self.__curve_updaters[filter_type][name], name)
                filterer.proxy().deregister(self.__label_updaters[filter_type][name], name)

if __name__ == "__main__":
    pg.setConfigOptions(antialias=True, background='w', foreground='k')
    app = QtGui.QApplication(sys.argv)
    leg_monitor_panel = LegMonitorPanel(0.05, 40, 800)
    app.aboutToQuit.connect(QtGui.QApplication.instance().quit)
    app.exec_()
    pykka.ActorRegistry.stop_all() # stop actors in LIFO order
    sys.exit()
