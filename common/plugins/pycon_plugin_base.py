from enum import Enum

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QMdiSubWindow, QMenu, QMenuBar, QVBoxLayout, QWidget

from common.logging.logger import logger
from plugins_std.pycon_time import PyConTime


class PyConPluginBase(QMdiSubWindow):

    class PyConLineInternalStatus(Enum):
        OK = "ok"
        NOT_OK = "not_ok"

    def __init__(self):
        super().__init__()

        self.__layout = None

        self.status: PyConPluginBase.PyConLineInternalStatus = PyConPluginBase.PyConLineInternalStatus.NOT_OK
        self.settings = {}

        self.__needed_signals = {}

    def initUI(self, widget: QWidget, opt_menubar: bool = False):
        self.__layout = QVBoxLayout()
        self.__layout.addWidget(widget)
        self.__widget = QWidget()
        self.__widget.setLayout(self.__layout)
        self.setWidget(self.__widget)

        if opt_menubar:
            self.__menu_bar = QMenuBar()
            self.__layout.setMenuBar(self.__menu_bar)

    def menubar(self):
        return self.__menu_bar

    def add_needed_signal(self, signal: str):
        self.__needed_signals[signal] = None

    def get_signal(self, signal) -> dict:
        return self.__needed_signals[signal]

    def needed_signals_names(self) -> list[str]:
        return self.__needed_signals.keys()

    def get_needed_signals(self):
        self.set_status_ok()
        for channel_name in self.__needed_signals.keys():
            try:
                self.__needed_signals[channel_name] = self.pycon_data_source.get_channel(channel_name=channel_name)

            except Exception as ex:
                logger().warning(str(ex))
                self.set_status_not_ok()

    def initialize(self):
        pass

    def get_settings(self):
        return self.settings

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
