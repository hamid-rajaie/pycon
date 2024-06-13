import sys
import traceback

import numpy as np
from PyQt5 import QtCore, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QSlider, QWidget

from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from plugins_std.pycon_time import PyConTime
from pycon_config import get_pycon_config


class PyConPluginControlPanel(PyConPluginBase):
    # ==================================================
    # SIGNALS
    # ==================================================
    control_panel_slider_value_changed = QtCore.pyqtSignal(PyConTime)

    def __init__(self):
        super().__init__()

        uic.loadUiType("plugins_std/pycon_plugin_control_panel.ui", self)
        self.setWindowTitle("Control Panel")

        self.int_min: int = 0
        self.int_max: int = 0

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
        self.slider_input.textChanged.connect(self.on_text_changed)

    @QtCore.pyqtSlot(int, int, str, np.ndarray, np.ndarray)
    def slot_add_signal_by_double_click(self, group_index, channel_index, channel_name, time, signal):
        self.set_slider_range(min_time=time[0], max_time=time[-1])

    def set_slider_range(self, min_time: float, max_time: float):
        logger().info(f"set slider range : [ {min_time}  {max_time} ]")

        min: float = min_time * get_pycon_config().pycon_conversion_factor__time_sec_to_msec
        max: float = max_time * get_pycon_config().pycon_conversion_factor__time_sec_to_msec

        __int_min: int = int(min)
        __int_max: int = int(max)

        diff: int = __int_max - __int_min

        try:
            if not self.has_range:
                self.slider.setMinimum(0)
                self.slider.setMaximum(diff)
                self.has_range = True
                self.int_min = __int_min
                self.int_max = __int_max
            else:
                if __int_min < self.int_min:
                    self.int_min = __int_min

                if __int_max > self.int_max:
                    self.slider.setMaximum(diff)
                    self.int_max = __int_max
        except OverflowError as exc:
            logger().error(str(exc))
            logger().error(f"{traceback.print_exception(type(exc), exc, exc.__traceback__)}")
            logger().error(f"min:{min} max:{max}")
            logger().error(f"int_min:{self.int_min} int_max:{self.int_max}")
        except Exception as exc:
            logger().error(type(exc))
            logger().error(str(exc))
            logger().error(f"min:{min} max:{max}")
            logger().error(f"int_min:{self.int_min} int_max:{self.int_max}")

    @QtCore.pyqtSlot(int)
    def on_slider_change(self, slider_value):

        value_abs: int = int(self.int_min + slider_value)
        value_diff: int = int(slider_value)

        self.slider_input.setText(str(value_diff))

        time = PyConTime(time=value_abs, time_diff=value_diff, unit=PyConTime.PyConTimeUnit.M_SEC)
        self.control_panel_slider_value_changed.emit(time)

    @QtCore.pyqtSlot(str)
    def on_text_changed(self, text: str):
        input_text = self.slider_input.text()
        self.slider.setValue(int(input_text))
