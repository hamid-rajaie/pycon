import numpy as np
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMdiSubWindow, QMenuBar, QVBoxLayout, QWidget

from common.logging.logger import logger
from common.plugins.pycon_plugin_signal_set import PyConPluginSignalSet
from plugins_std.pycon_time import PyConTime


class PyConPluginBase(QMdiSubWindow, PyConPluginSignalSet):

    def __init__(self):
        super().__init__()

        self.__layout = None

        self.settings = {}

    def initUI(self, widget: QWidget, with_menubar: bool):
        self.__layout = QVBoxLayout()
        self.__layout.addWidget(widget)
        self.__widget = QWidget()
        self.__widget.setLayout(self.__layout)
        self.setWidget(self.__widget)

        if with_menubar:
            self.__menu_bar = QMenuBar()
            self.__layout.setMenuBar(self.__menu_bar)

    def menubar(self):
        return self.__menu_bar

    def initialize(self):
        pass

    def get_settings(self):
        return self.settings

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
