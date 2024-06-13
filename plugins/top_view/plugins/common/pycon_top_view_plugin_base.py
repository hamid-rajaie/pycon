import matplotlib.axes as axes
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMdiSubWindow

from common.logging.logger import logger


class PyConTopViewPluginBase:
    def __init__(self, name: str):
        super().__init__()

        self.name = name

    def load_signals(self):
        raise Exception("load_signals is not implemented")

    def init(self, ax: axes, plot_lines: list):
        raise Exception("init is not implemented")

    def draw(self, time_sec, plot_lines: list):
        raise Exception("draw is not implemented")

    def plot_data(self, ax, x, y, marker, color, linewidth, markersize, label):
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html#matplotlib.axes.Axes.plot
        # return : list of Line2D : https://matplotlib.org/stable/api/_as_gen/matplotlib.lines.Line2D.html#matplotlib.lines.Line2D
        return ax.plot(
            x,
            y,
            marker=marker,
            color=color,
            linewidth=linewidth,
            markersize=markersize,
            label=label,
        )
