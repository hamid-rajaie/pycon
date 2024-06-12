import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMdiSubWindow

from common.logging.logger import logger


class PyConPluginBase(QMdiSubWindow):
    def __init__(self):
        super().__init__()

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

    @QtCore.pyqtSlot(int, int)
    def slider_value_changed(self, time_msec, time_diff_sec):
        pass
