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

TOP_FLUID_PRESSURE_MIN = 0
TOP_FLUID_PRESSURE_MAX = 60
BOTTOM_FLUID_PRESSURE_MIN = 30
BOTTOM_FLUID_PRESSURE_MAX = 90

class LegMonitorPanel(QtGui.QMainWindow):
    def __init__(self, update_interval, filter_width, graph_width):
        super().__init__()
        self.update_interval = update_interval
        self.__ui = uic.loadUi(_UI_LAYOUT_PATH)
        self.__ui.show()
        self.__init_window()

        self._sensors = {'fluid pressure'}
        self._display_components = {
            'top fluid pressure': ('fluid pressure', 0),
            'bottom fluid pressure': ('fluid pressure', 1)
        }

        self.__init_graphs()
        self.__init_curve_updaters(graph_width)

        self.__init_labels()
        self.__init_label_updaters()

        self.__init_filters(filter_width, graph_width)
        self.__init_unit_conversion()

        self.__monitor = None

    def __init_window(self):
        # Actions
        self.__ui.actionExit.triggered.connect(QtGui.QApplication.instance().quit)
        self.__ui.actionConnect.triggered.connect(self.__init_monitoring)
        self.__ui.actionStartMonitoring.setDisabled(True)
        self.__ui.actionStartMonitoring.triggered.connect(self.__start_monitoring)
        self.__ui.actionStopMonitoring.setDisabled(True)
        self.__ui.actionStopMonitoring.triggered.connect(self.__stop_monitoring)
        self.__ui.actionAdditionalPlots.toggled.connect(self.__toggle_additional_plots)
        self.__ui.actionAdditionalPlots.setDisabled(True)
        self.__ui.actionSaveScreenshot.triggered.connect(self.__screenshot)

    def __init_graphs(self):
        self.__graphs = {
            'top fluid pressure': self.__ui.topFluidPlot.getPlotItem(),
            'bottom fluid pressure': self.__ui.bottomFluidPlot.getPlotItem()
        }
        for (_, graph) in self.__graphs.items():
            graph.disableAutoRange(axis=pg.ViewBox.YAxis)
            #graph.addLegend()
        self.__graphs['top fluid pressure'].getViewBox().setYRange(TOP_FLUID_PRESSURE_MIN,
                                                                   TOP_FLUID_PRESSURE_MAX)
        self.__graphs['top fluid pressure'].setTitle("Fluid Pressure Above Vein")
        self.__graphs['top fluid pressure'].setLabels(left="Pressure (mmHg)")
        self.__graphs['bottom fluid pressure'].getViewBox().setYRange(BOTTOM_FLUID_PRESSURE_MIN,
                                                                      BOTTOM_FLUID_PRESSURE_MAX)
        self.__graphs['bottom fluid pressure'].setTitle("Fluid Pressure Below Vein")
        self.__graphs['bottom fluid pressure'].setLabels(left="Pressure (mmHg)")

    def __init_labels(self):
        self.__denoised_labels = {
            'top fluid pressure': self.__ui.topFluidValue,
            'bottom fluid pressure': self.__ui.bottomFluidValue
        }
        self.__max_labels = {
            'top fluid pressure': self.__ui.topFluidMax,
            'bottom fluid pressure': self.__ui.bottomFluidMax
        }
        self.__min_labels = {
            'top fluid pressure': self.__ui.topFluidMin,
            'bottom fluid pressure': self.__ui.bottomFluidMin
        }

    def __init_curve_updaters(self, graph_width):
        self.__curve_types = {
            'raw': {
                'pen': 'r',
                'name': 'Raw'
            },
            'denoised': {
                'pen': 'k',
                'name': 'Pressure'
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
        for name in self._display_components:
            for (curve_type, curve_props) in self.__curve_types.items():
                curve = self.__graphs[name].plot(pen=curve_props['pen'], name=curve_props['name'])
                curve_updater = plotting.CurveUpdater.start(curve, graph_width)
                if curve_type != 'denoised':
                    curve_updater.tell({'command': 'hide'})
                self.__curve_updaters[curve_type][name] = curve_updater

    def __init_label_updaters(self):
        self.__label_updaters = {
            'denoised': {},
            'max': {},
            'min': {}
        }
        for name in self._display_components:
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
        for name in self._display_components:
            filterer = signal.Filterer.start(filter_width)
            self.__filterers['denoised'][name] = filterer
            maximizer = signal.Filterer.start(graph_width // 4, max, "right")
            self.__filterers['max'][name] = maximizer
            filterer.proxy().register(maximizer, name)
            minimizer = signal.Filterer.start(graph_width // 4, min, "right")
            self.__filterers['min'][name] = minimizer
            filterer.proxy().register(minimizer, name)

    def __init_unit_conversion(self):
        self.__unit_converter = leg.LegUnitConverter.start()
        self.__tuple_selectors = {}
        for (name, properties) in self._display_components.items():
            tuple_selector = signal.TupleSelector.start(properties[1], name)
            self.__unit_converter.proxy().register(tuple_selector, properties[0])
            tuple_selector.proxy().register(self.__filterers['denoised'][name],
                                            name)
            self.__tuple_selectors[name] = tuple_selector

    def __init_monitoring(self):
        self.__ui.statusbar.showMessage("Connecting...")
        try:
            monitor = leg.LegMonitor.start()
            self.__monitor = monitor
        except RuntimeError as e:
            self.__ui.statusbar.showMessage(str(e))
            logging.error(e, exc_info=True)
            return
        self.__ui.statusbar.showMessage("Established connection over "
                                        "{}".format(monitor.proxy().connection_device.get()))
        for name in self._sensors:
            self.__monitor.proxy().register(self.__unit_converter, name)
        self.__ui.actionConnect.setDisabled(True)
        self.__ui.actionStartMonitoring.setDisabled(False)
        self.__ui.actionAdditionalPlots.setDisabled(False)
        self.__ui.actionStartMonitoring.trigger()

    def __start_monitoring(self):
        for name in self._display_components:
            raw_curve_updater = self.__curve_updaters['raw'][name]
            raw_curve_updater.tell({'command': 'clear'})
            self.__tuple_selectors[name].proxy().register(raw_curve_updater, name)
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
        for name in self._display_components:
            raw_curve_updater = self.__curve_updaters['raw'][name]
            self.__tuple_selectors[name].proxy().deregister(raw_curve_updater, name)
            for filter_type in self.__filterers.keys():
                filterer = self.__filterers[filter_type][name]
                filterer.proxy().deregister(self.__curve_updaters[filter_type][name], name)
                filterer.proxy().deregister(self.__label_updaters[filter_type][name], name)

    def __toggle_additional_plots(self, show_additional):
        for curve_type in self.__curve_types:
            if curve_type != 'denoised':
                for name in self._display_components:
                    curve_updater = self.__curve_updaters[curve_type][name]
                    if show_additional:
                        curve_updater.tell({'command': 'show'})
                    else:
                        curve_updater.tell({'command': 'hide'})

    def __screenshot(self):
        image = QtGui.QImage(self.__ui.centralwidget.size(), QtGui.QImage.Format_RGB32)
        painter = QtGui.QPainter(image)
        self.__ui.centralwidget.render(painter)
        save_dialog = QtGui.QFileDialog()
        save_dialog.setWindowTitle("Save screenshot")
        save_dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        save_dialog.setNameFilter("PNG images (*.png)")
        save_dialog.setDefaultSuffix('png')
        if save_dialog.exec():
            filename = save_dialog.selectedFiles()[0]
            image.save(filename, format="PNG")
            self.__ui.statusbar.showMessage("Saved screenshot to {}".format(filename))
        painter.end()

if __name__ == "__main__":
    pg.setConfigOptions(antialias=True, background='w', foreground='k')
    app = QtGui.QApplication(sys.argv)
    leg_monitor_panel = LegMonitorPanel(0.05, 20, 800)
    app.aboutToQuit.connect(QtGui.QApplication.instance().quit)
    app.exec_()
    pykka.ActorRegistry.stop_all() # stop actors in LIFO order
    sys.exit()
