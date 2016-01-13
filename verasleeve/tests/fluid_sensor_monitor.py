#!/usr/bin/env python3
"""Tests creation of a simple GUI with PyQt."""
# Python imports
import sys
import os

# Dependency imports
import pykka
import pyqtgraph as pg
from pyqtgraph.Qt import uic
from pyqtgraph.Qt import QtGui

# Package imports
from .. import leg, signal, plotting

_UI_LAYOUT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sensor_monitor.ui')

class LabelUpdater(pykka.ThreadingActor):
    """Updates a Qt label with sample data."""
    def __init__(self, label):
        super().__init__()
        self.label = label

    def on_receive(self, message):
        """Slot that updates the text label with the next sample."""
        self.label.setText("{}: {}".format(message['data'], message[message['data']]))

class SensorMonitor(QtGui.QMainWindow):
    def __init__(self, update_interval, filter_width, max_samples):
        super().__init__()
        self.__ui = uic.loadUi(_UI_LAYOUT_PATH)
        self.__ui.show()
        self.__init_window()
        self.__init_monitor(update_interval, filter_width, max_samples)

    def __init_window(self):
        # Actions
        self.__ui.actionExit.triggered.connect(QtGui.QApplication.instance().quit)

    def __init_monitor(self, update_interval, filter_width, max_samples):
        graph = self.__ui.signalPlot.getPlotItem()
        graph.getViewBox().disableAutoRange(axis=pg.ViewBox.YAxis)
        graph.getViewBox().setYRange(50, 400)
        graph.addLegend()
        graph.setTitle("Fluid Pressure Sensor Reading")
        graph.setLabels(bottom="Time (s)", left="Pin Value (0-1024)")
        signal_curve = graph.plot(pen='r', name="Raw (Noisy) Signal")
        filtered_curve = graph.plot(pen='b', name="Median Filtered Signal")

        signal_curve_updater = plotting.CurveUpdater.start(signal_curve, max_samples)
        filtered_curve_updater = plotting.CurveUpdater.start(filtered_curve,
                                                                          max_samples)
        filtered_label_updater = LabelUpdater.start(self.__ui.signalValue)
        signal_filter = signal.Filterer.start(filter_width)
        signal_filter.proxy().register(filtered_curve_updater, 'fluid pressure')
        signal_filter.proxy().register(filtered_label_updater, 'fluid pressure')

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
    app = QtGui.QApplication(sys.argv)
    sensor_monitor = SensorMonitor(0.05, 40, 100)
    app.exec_()
    pykka.ActorRegistry.stop_all() # stop actors in LIFO order
    sys.exit()
