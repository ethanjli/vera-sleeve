#!/usr/bin/env python3
"""Monitors the fluid pressure sensor reading."""
# Python imports
import sys
import os
import logging

# Dependency imports
import pykka
from PyQt4 import uic, QtGui

# Package imports
from verasleeve import sleeve

logging.basicConfig(level=logging.INFO)

_UI_LAYOUT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sleeve_panel.ui')

class SleevePanel(QtGui.QMainWindow):
    def __init__(self, update_interval):
        super().__init__()
        self.update_interval = update_interval
        self.__ui = uic.loadUi(_UI_LAYOUT_PATH)
        self.__ui.show()
        self.__init_window()

        self.__sleeve_servos = None
        self._controllers = {'Additive': None, 'Independent': None}
        self._active_controller = 'Additive'

    def __init_window(self):
        # Actions
        self.__ui.actionExit.triggered.connect(self.quit)
        self.__ui.actionConnect.triggered.connect(self.__init_controllers)
        self.__ui.actionStartRunning.setDisabled(True)
        self.__ui.actionStartRunning.triggered.connect(self.__start_running)
        self.__ui.actionStopRunning.setDisabled(True)
        self.__ui.actionStopRunning.triggered.connect(self.__stop_running)
        # Sleeve parameter widgets
        self.__ui.patternComboBox.currentIndexChanged.connect(self.__set_pattern)
        self.__ui.patternComboBox.setDisabled(True)
        self.__ui.periodSpinBox.valueChanged.connect(self.__set_period)
        self.__ui.periodSpinBox.setDisabled(True)
        self.__ui.dutySpinBox.valueChanged.connect(self.__set_duty)
        self.__ui.dutySpinBox.setDisabled(True)
        self.__ui.delaySpinBox.valueChanged.connect(self.__set_delay)
        self.__ui.delaySpinBox.setDisabled(True)
        self.__ui.uncontractedSpinBox.valueChanged.connect(self.__set_uncontracted)
        self.__ui.uncontractedSpinBox.setDisabled(True)
        self.__ui.contractedSpinBox.valueChanged.connect(self.__set_contracted)
        self.__ui.contractedSpinBox.setDisabled(True)

    def __init_controllers(self):
        self.__ui.statusbar.showMessage("Connecting...")
        try:
            sleeve_servos = sleeve.SleeveServos()
            self.__sleeve_servos = sleeve_servos
        except RuntimeError as e:
            self.__ui.statusbar.showMessage(str(e))
            logging.error(e, exc_info=True)
            return
        self.__ui.statusbar.showMessage("Established connection over "
                                        "{}".format(sleeve_servos.connection_device))
        self._controllers['Additive'] = sleeve.AdditiveSleeveController.start(self.__sleeve_servos)
        self._controllers['Independent'] = sleeve.IndependentSleeveController.start(self.__sleeve_servos)
        self._active_controller = 'Additive'
        self.__ui.actionConnect.setDisabled(True)
        self.__ui.actionStartRunning.setDisabled(False)
        self.__ui.actionStartRunning.trigger()
        self.__ui.patternComboBox.setDisabled(False)
        self.__ui.periodSpinBox.setDisabled(False)
        self.__ui.dutySpinBox.setDisabled(False)
        self.__ui.delaySpinBox.setDisabled(False)
        self.__ui.uncontractedSpinBox.setDisabled(False)
        self.__ui.contractedSpinBox.setDisabled(False)

    def __start_running(self):
        controller = self._controllers[self._active_controller]
        controller.tell({'command': 'start producing', 'interval': self.update_interval})
        controller_proxy = controller.proxy()
        self.__ui.periodSpinBox.setValue(controller_proxy.period.get())
        self.__ui.dutySpinBox.setValue(controller_proxy.duty.get())
        self.__ui.delaySpinBox.setValue(controller_proxy.delay_per_band.get())
        self.__ui.uncontractedSpinBox.setValue(controller_proxy.uncontracted_pos.get())
        self.__ui.contractedSpinBox.setValue(controller_proxy.contracted_pos.get())
        self.__ui.actionStartRunning.setDisabled(True)
        self.__ui.actionStopRunning.setDisabled(False)
        self.__ui.statusbar.showMessage("Started {}".format(self._active_controller))
    def __stop_running(self, block=False):
        if block:
            self._controllers[self._active_controller].ask({'command': 'stop producing'})
        else:
            self._controllers[self._active_controller].tell({'command': 'stop producing'})
        self.__ui.actionStartRunning.setDisabled(False)
        self.__ui.actionStopRunning.setDisabled(True)
        self.__ui.statusbar.showMessage("Stopped {}".format(self._active_controller))

    def quit(self):
        active_controller = self._controllers[self._active_controller]
        if active_controller is not None:
            active_controller.stop(block=True)
            self._controllers[self._active_controller] = None
            for (_, controller) in self._controllers.items():
                if controller is not None:
                    controller.proxy().sleeve_servos = None
        QtGui.QApplication.instance().quit()

    # Sleeve parameter slots
    def __set_pattern(self, _):
        new_active_controller = self.__ui.patternComboBox.currentText()
        if self._active_controller != new_active_controller:
            self.__stop_running(block=True)
            self._active_controller = new_active_controller
            self.__start_running()
    def __set_period(self):
        active_controller = self._controllers[self._active_controller].proxy()
        active_controller.period = self.__ui.periodSpinBox.value()
    def __set_duty(self):
        active_controller = self._controllers[self._active_controller].proxy()
        active_controller.duty = self.__ui.dutySpinBox.value()
    def __set_delay(self):
        active_controller = self._controllers[self._active_controller].proxy()
        active_controller.delay_per_band = self.__ui.delaySpinBox.value()
    def __set_uncontracted(self):
        active_controller = self._controllers[self._active_controller].proxy()
        active_controller.uncontracted_pos = self.__ui.uncontractedSpinBox.value()
    def __set_contracted(self):
        active_controller = self._controllers[self._active_controller].proxy()
        active_controller.contracted_pos = self.__ui.contractedSpinBox.value()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    sleeve_panel = SleevePanel(0.05)
    app.aboutToQuit.connect(sleeve_panel.quit)
    app.exec_()
    pykka.ActorRegistry.stop_all() # stop actors in LIFO order
    sys.exit()
