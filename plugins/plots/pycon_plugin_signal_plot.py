import numpy as np
from matplotlib import gridspec, rc, rcParams
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5 import QtCore, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QWidget

from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from plugins_std.pycon_time import PyConTime
from pycon_config import get_pycon_config


class PyConWindowSignalPlot(PyConPluginBase):

    def __init__(self, params: PyConPluginParams):
        super().__init__()

        uic.loadUiType("plugins/plots/pycon_plugin_signal_plot.ui", self)
        self.setWindowTitle("Signal Plot")

        self.widget_1 = None
        self.widget_2 = None

        self.row = 0
        self.axes_dict = {}

        self.highlighted_plot_lines = {}
        self.current_time_msec = None

        self.__initUI()

    def __initUI(self):
        self.widget_1 = QWidget()
        self.widget_1_layout = QGridLayout(self.widget_1)

        pal_1 = self.widget_1.palette()
        self.widget_1.setAutoFillBackground(True)
        pal_1.setColor(self.widget_1.backgroundRole(), Qt.white)
        self.widget_1.setPalette(pal_1)
        #
        # create a layout, containing :
        #
        _layout = QVBoxLayout()
        _layout.addWidget(self.widget_1)
        #
        # widget of self
        #
        _widget = QWidget()
        _widget.setLayout(_layout)
        self.setWidget(_widget)

        # a figure instance to plot on
        self.figure = Figure()
        self.figure.tight_layout()

        # store the plot handle to update later
        self.canvas = FigureCanvas(self.figure)
        # add the navigation toolbar
        self.nav_toolbar = NavigationToolbar(self.canvas, self)
        self.widget_1_layout.addWidget(self.nav_toolbar)
        self.widget_1_layout.addWidget(self.canvas)
        self.canvas.draw()

    @QtCore.pyqtSlot(int, int, str, np.ndarray, np.ndarray)
    def slot_add_signal_by_double_click(self, group_index, channel_index, channel_name, time, signal):
        x_points = time * get_pycon_config().pycon_conversion_factor__time_sec_to_msec
        y_points = signal

        try:
            ax = self.get_new_axis(plot_name=channel_name, x_label="time")
            # ax.plot(x_points, y_points, label=channel_name, color="blue", linewidth=0.5)
            ax.plot(x_points, y_points, color="blue", linewidth=0.5)
            # ax.legend()
        except Exception as e:
            logger().warning(f"PyConWindowSignalSeriesPlot.display_csv_selected_signal   {e}")

        self.canvas.draw()

    def get_new_axis(self, plot_name: str, x_label: str):
        # https://matplotlib.org/stable/api/figure_api.html
        # axis is single
        # https://matplotlib.org/stable/api/axis_api.html
        # axes is plural
        # https://matplotlib.org/stable/api/axes_api.html

        if len(self.figure.get_axes()) == 0:
            self.row = 1
            ax = self.figure.add_subplot(self.row, 1, 1)
        else:
            self.row += 1
            gs = gridspec.GridSpec(self.row, 1)
            # Reposition existing subplots
            for i, ax in enumerate(self.figure.axes):
                ax.set_position(gs[i].get_position(self.figure))
                ax.set_subplotspec(gs[i])

            ax = self.figure.add_subplot(gs[self.row - 1])
            self.axes_dict[plot_name] = ax

        ax.set_title(plot_name, fontsize=8, color="green")
        # ax.set_xlabel(x_label, fontsize=8)
        ax.tick_params(axis="both", which="major", labelsize=6)
        ax.tick_params(axis="both", which="minor", labelsize=4)
        ax.tick_params(width=1)
        # ax.set_ylabel(plot_name, fontsize=4)

        return ax

    @QtCore.pyqtSlot(PyConTime)
    def slider_value_changed(self, time: PyConTime):
        """Updates or adds a vertical line at time_msec across all subplots."""
        self.current_time_msec = time.get_time_msec()
        self.__ensure_highlighted_lines()  # Ensure all subplots have a line

        # Update the position of the line in each subplot
        for ax, line in self.highlighted_plot_lines.items():
            line.set_xdata([time.time, time.time])

        self.canvas.draw()

    def __ensure_highlighted_lines(self):
        """Ensure that all axes in the figure have a highlighted line."""
        current_axes = set(self.figure.axes)
        # if not hasattr(self, "highlighted_plot_lines"):
        #    self.highlighted_plot_lines = {}

        # Add lines to new axes
        for ax in current_axes:
            if ax not in self.highlighted_plot_lines:
                self.highlighted_plot_lines[ax] = ax.axvline(
                    x=self.current_time_msec, color="green", linewidth=0.5, linestyle="--"
                )

        # Remove lines from removed axes
        for ax in list(self.highlighted_plot_lines):
            if ax not in current_axes:
                self.highlighted_plot_lines.pop(ax).remove()
