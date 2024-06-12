from enum import Enum, IntEnum

import numpy as np
from PyQt5 import QtCore, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QMdiSubWindow, QSlider, QWidget

from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from pycon_config import get_pycon_config


class PyConWindowControlPanel(PyConPluginBase):
    # ==================================================
    # SIGNALS
    # ==================================================
    control_panel_slider_value_changed = QtCore.pyqtSignal(int, int)

    class RangeMode(IntEnum):
        COMPARE = 0
        NO_COMPARE = 1

    def __init__(self):
        super().__init__()

        uic.loadUiType("plugins_std/pycon_window_control_panel.ui", self)
        self.setWindowTitle("Control Panel")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.has_range = False

        self.slider_input = QLineEdit()

        self.slider_widget = QWidget()

        layout = QHBoxLayout()
        layout.addWidget(self.slider_input)
        layout.addWidget(self.slider)
        self.slider_widget.setLayout(layout)

        self.setWidget(self.slider_widget)

        self.slider.valueChanged.connect(self.on_slider_change)
        self.slider_input.textChanged.connect(self.slider_input_changed)

    @QtCore.pyqtSlot(int, int, str, np.ndarray, np.ndarray)
    def slot_add_signal_by_double_click(self, group_index, channel_index, channel_name, time, signal):
        logger().warning("derived class")
        self.set_slider_range(
            min_time=time[0],
            max_time=time[-1],
            range_mode=PyConWindowControlPanel.RangeMode.COMPARE,
        )

    @QtCore.pyqtSlot(float, float, RangeMode)
    def set_slider_range(self, min_time: float, max_time: float, range_mode: RangeMode):
        min = min_time * get_pycon_config().pycon_conversion_factor__time
        max = max_time * get_pycon_config().pycon_conversion_factor__time

        int_min = int(min)
        int_max = int(max)

        logger().info(f"new slider range : {int_min}:{int_max}")

        try:
            if range_mode == PyConWindowControlPanel.RangeMode.NO_COMPARE:
                self.slider.setMinimum(int_min)
                self.slider.setMaximum(int_max)
                # self.has_range = True
            else:
                if not self.has_range:
                    self.slider.setMinimum(int_min)
                    self.slider.setMaximum(int_max)
                    self.has_range = True
                else:
                    if int_min < self.slider.minimum():
                        logger().info(f"update min : {int_min}")
                        self.slider.setMinimum(int_min)
                    if int_max > self.slider.maximum():
                        logger().info(f"update max : {int_max}")
                        self.slider.setMaximum(int_max)
        except Exception as ex:
            logger().warning(str(ex))
            logger().warning(f"min:{min} max:{max}")
            logger().warning(f"int_min:{int_min} int_max:{int_max}")

    def set_value(self, value):
        self.slider.setValue(value)

    def value(self):
        return self.slider.value()

    def on_slider_change(self, value):
        self.slider_input.setText(str(value))

        value_diff = value - self.slider.minimum()
        self.control_panel_slider_value_changed.emit(value, value_diff)

    def slider_input_changed(self):
        input_text = self.slider_input.text()
        if input_text in ["-", "+", ""]:
            self.slider.setValue(0)
        else:
            self.slider.setValue(int(input_text))
