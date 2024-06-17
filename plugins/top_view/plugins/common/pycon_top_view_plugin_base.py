from enum import Enum

import matplotlib.axes as axes
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.lines import Line2D
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMdiSubWindow

from common.logging.logger import logger


class PyConTopViewPluginBase:

    class PyConLineInternalStatus(Enum):
        OK = "ok"
        NOT_OK = "not_ok"

    def __init__(self, name: str):
        super().__init__()

        self.name = name
        self.status: PyConTopViewPluginBase.PyConLineInternalStatus = (
            PyConTopViewPluginBase.PyConLineInternalStatus.NOT_OK
        )

    def init_data(self):
        pass

    def set_status_ok(self):
        self.status: PyConTopViewPluginBase.PyConLineInternalStatus = PyConTopViewPluginBase.PyConLineInternalStatus.OK

    def set_status_not_ok(self):
        self.status: PyConTopViewPluginBase.PyConLineInternalStatus = (
            PyConTopViewPluginBase.PyConLineInternalStatus.NOT_OK
        )

    def is_status_ok(self):
        if self.status == PyConTopViewPluginBase.PyConLineInternalStatus.OK:
            return True
        return False

    def is_status_not_ok(self):
        if self.status == PyConTopViewPluginBase.PyConLineInternalStatus.NOT_OK:
            return True
        return False

    def init(self, ax: axes, lines_2d: list):
        raise Exception("init is not implemented")

    def render(self, time_sec, lines_2d: list):
        raise Exception("render is not implemented")

    def plot_data(self, ax: axes, x_array, y_array, color, linewidth, markersize, label, marker=None):
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.html#matplotlib.axes.Axes
        #
        # https://matplotlib.org/stable/api/axes_api.html
        #
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html#matplotlib.axes.Axes.plot
        # return : list of Line2D : https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D

        line_2d_list: list[Line2D] = ax.plot(
            x_array,
            y_array,
            marker=marker,
            color=color,
            linewidth=linewidth,
            markersize=markersize,
            label=label,
        )

        # logger().info(f"type of line_2d_list : {type(line_2d_list)}, len : {len(line_2d_list)}")
        # logger().info(f"type of line_2d_list : {type(line_2d_list[0])}")

        return line_2d_list
