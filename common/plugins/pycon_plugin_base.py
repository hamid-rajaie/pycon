from enum import Enum

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMdiSubWindow

from common.logging.logger import logger
from plugins_std.pycon_time import PyConTime


class PyConPluginBase(QMdiSubWindow):

    class PyConLineInternalStatus(Enum):
        OK = "ok"
        NOT_OK = "not_ok"

    def __init__(self):
        super().__init__()

        self.status: PyConPluginBase.PyConLineInternalStatus = PyConPluginBase.PyConLineInternalStatus.NOT_OK

    def init_data(self):
        pass

    def set_status_ok(self):
        self.status: PyConPluginBase.PyConLineInternalStatus = PyConPluginBase.PyConLineInternalStatus.OK

    def set_status_not_ok(self):
        self.status: PyConPluginBase.PyConLineInternalStatus = PyConPluginBase.PyConLineInternalStatus.NOT_OK

    def is_status_ok(self):
        if self.status == PyConPluginBase.PyConLineInternalStatus.OK:
            return True
        return False

    def is_status_not_ok(self):
        if self.status == PyConPluginBase.PyConLineInternalStatus.NOT_OK:
            return True
        return False

    def eventFilter(self, obj, event):
        if obj == self.widget() and event.type() == event.Close and obj.close():
            self.close()
            return True
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        logger().info("")
        super().showEvent(event)
        if self.widget() and self.widget().isHidden():
            self.widget().show()

    @QtCore.pyqtSlot(int, int, str, np.ndarray, np.ndarray)
    def slot_add_signal_by_double_click(self, group_index, channel_index, channel_name, time, signal):
        pass

    @QtCore.pyqtSlot(PyConTime)
    def slider_value_changed(self, time: PyConTime):
        pass
