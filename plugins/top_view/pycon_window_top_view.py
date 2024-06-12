import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtCore, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (
    QColorDialog,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMdiSubWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from common.pycon_numpy import find_nearest_time
from pycon_config import get_pycon_config


class PyConWindowTopView(PyConPluginBase):

    def __init__(self, params: PyConPluginParams):
        QMdiSubWindow.__init__(self)

        uic.loadUiType("plugins/top_view/pycon_window_top_view.ui", self)
        self.setWindowTitle("Top View")
        self.resize(500, 700)

        self.pycon_app_data_source = params.pycon_app_data_source

        self.internal_status = False

        self.widget_1 = None
        self.widget_2 = None

        self.mapping = {
            # (signal_name, plot_lines, label)
            "video_lines": [
                ("left", 0, "ego"),
                ("right", 1, "ego"),
                ("leftLeft", 2, "neighbour"),
                ("rightRight", 3, "neighbour"),
                ("roadEdgeLeft", 4, "road_edges"),
                ("roadEdgeRight", 5, "road_edges"),
            ],
            "gt_lines": [
                ("EgoLeft", 6, "gt_ego"),
                ("EgoRight", 7, "gt_ego"),
                ("EgoMean", 8, "gt_ego_mean"),
                ("RoadEdgeLeft", 9, "gt_road_edge"),
                ("RoadEdgeRight", 10, "gt_road_edge"),
            ],
            "map_sensor": [("mapSensor.roadSegmentGeometryCollection", 11, "map_ref_line")],
        }

        self.plot_colors = {
            "map_ref_line": "blue",
            "ego": "green",
            "neighbour": "#FDF207",
            "road_edges": "magenta",
            "gt_ego": "black",
            "gt_ego_mean": "red",
            "gt_road_edge": "black",
        }

        self.__initUI()
        self.__load_signals()
        self.create_top_view()

    def __initUI(self):
        self.widget_1 = QWidget()
        self.widget_1_layout = QGridLayout(self.widget_1)

        self.widget_2 = QWidget()

        pal_1 = self.widget_1.palette()
        self.widget_1.setAutoFillBackground(True)
        pal_1.setColor(self.widget_1.backgroundRole(), Qt.white)
        self.widget_1.setPalette(pal_1)

        pal_2 = self.widget_2.palette()
        self.widget_2.setAutoFillBackground(True)
        pal_2.setColor(self.widget_2.backgroundRole(), Qt.yellow)
        self.widget_2.setPalette(pal_2)
        #
        # create a layout, containing :
        #  1. the table widget
        #  2. the tree view
        #
        _layout = QVBoxLayout()
        _layout.addWidget(self.widget_1)
        # _layout.addWidget(self.widget_2, 3)
        #
        # widget of self
        #
        _widget = QWidget()
        _widget.setLayout(_layout)
        self.setWidget(_widget)

    def __load_signals(self):
        try:
            line = "left"
            latDeviation = f"videoLines.{line}.clothoid.latDeviation"
            curvature = f"videoLines.{line}.clothoid.curvature"
            curvatureChange = f"videoLines.{line}.clothoid.curvatureChange"
            headingAngle = f"videoLines.{line}.clothoid.headingAngle"
            startPositionX = f"videoLines.{line}.startPositionX"
            lookAheadDistance = f"videoLines.{line}.lookAheadDistance"

            self.time = self.pycon_app_data_source.get_channel(channel_name="timestamp")
            self.latDeviation = self.pycon_app_data_source.get_channel(channel_name=latDeviation)
            self.curvature = self.pycon_app_data_source.get_channel(channel_name=curvature)
            self.curvatureChange = self.pycon_app_data_source.get_channel(channel_name=curvatureChange)
            self.headingAngle = self.pycon_app_data_source.get_channel(channel_name=headingAngle)
            self.startPositionX = self.pycon_app_data_source.get_channel(channel_name=startPositionX)
            self.lookAheadDistance = self.pycon_app_data_source.get_channel(channel_name=lookAheadDistance)

            self.internal_status = True

        except Exception as ex:
            logger().warning(str(ex))

    def plot_data(self, ax, x, y, marker, color, linewidth, markersize, label):
        """provide the plot for a given lane with x,y coordinates"""

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

    def create_top_view(self):

        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
        # https://matplotlib.org/stable/api/axes_api.html
        fig, ax = plt.subplots()
        # fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

        self.plot_lines = []
        """
        x_array, y_array = self.provide_clothoid_values(
            latDeviation=0,
            curvature=0,
            curvatureChange=0,
            headingAngle=0,
            startPositionX=0,
            lookAheadDistance=0,
        )
        """

        x_array = np.arange(-50, 50, 1, dtype=float)
        y_array = np.arange(0, 100, 1, dtype=float)

        lines = self.plot_data(
            ax=ax, x=x_array, y=y_array, marker="o", color="blue", linewidth=0.5, markersize=2, label="left"
        )
        logger().info(f"type of plot_data ret : {type(lines)}, len : {len(lines)}")

        self.plot_lines.append(lines[0])

        # ax.set_xlabel("y distance [m]")
        # ax.set_ylabel("x distance [m]")
        # ax.set_xlim(-15, 15)
        # ax.set_ylim(-5, 105)
        # ax.set_title(f"GT Plot idx: {self.control_panel.value()}")

        # store the plot handle to update later
        self.canvas = FigureCanvas(fig)
        # add the navigation toolbar
        self.nav_toolbar = NavigationToolbar(self.canvas, self)
        self.widget_1_layout.addWidget(self.nav_toolbar)
        self.widget_1_layout.addWidget(self.canvas)
        self.canvas.draw()
        # self.resize(600, 700)

    @QtCore.pyqtSlot(int, int)
    def slider_value_changed(self, time_msec, time_diff_sec):

        if self.internal_status == False:
            return

        time_sec = time_msec / get_pycon_config().pycon_conversion_factor__time

        idx, t = find_nearest_time(arr=self.time.samples, value=time_sec)

        latDeviation = self.latDeviation.samples[idx]
        curvature = self.curvature.samples[idx]
        curvatureChange = self.curvatureChange.samples[idx]
        headingAngle = self.headingAngle.samples[idx]
        startPositionX = self.startPositionX.samples[idx]
        lookAheadDistance = self.lookAheadDistance.samples[idx]

        if hasattr(self, "plot_lines"):

            logger().info(f"draw @ time_msec:{time_msec}  idx:{idx}")

            x_array, y_array = self.provide_clothoid_values(
                latDeviation=latDeviation,
                curvature=curvature,
                curvatureChange=curvatureChange,
                headingAngle=headingAngle,
                startPositionX=startPositionX,
                lookAheadDistance=lookAheadDistance,
            )
            line_index = 0

            self.plot_lines[line_index].set_xdata(x_array)
            self.plot_lines[line_index].set_ydata(y_array)
            self.plot_lines[line_index].set_color("blue")

            # ax = self.plot_lines[0][0].axes
            # title = f"GT Plot idx: {val} [{self.df.iloc[int(val)]['timestamp']}s]"
            # if self.adma_available:
            #    title += f"\nLocation: ({round(self.df.iloc[int(val)]['lat_wgs84'], 5)}|{round(self.df.iloc[int(val)]['lon_wgs84'],5)})"
            # ax.set_title(title)
            self.canvas.draw()

            logger().info("====================================================")

    def approx_clothoid(self, clothoid, x):
        """provide the y value for a given
        x value, considering the clothoid params
        :clothoid: clothoid parameters [hA,c0,c1,dy]
        :x: x value
        return approx y value
        """
        x_cs = x / np.cos(clothoid[0])
        L = x_cs + 1 / 6 * x_cs**3 * clothoid[1] ** 2
        y_cs = L**2 * (1 / 2 * clothoid[1] + 1 / 6 * clothoid[2] * L)
        y = np.sin(clothoid[0]) * x_cs + np.cos(clothoid[0]) * y_cs + clothoid[3]

        return y

    def provide_clothoid_values(
        self,
        latDeviation: float,
        curvature: float,
        curvatureChange: float,
        headingAngle: float,
        startPositionX: float,
        lookAheadDistance: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """provide the x,y values for a given line
        :row: df row
        :line: name of line
        return x, y
        """

        dy = latDeviation
        c0 = curvature
        c1 = curvatureChange
        hA = headingAngle
        x0 = startPositionX
        x1 = lookAheadDistance

        if x1 - x0 > 0:
            # calculate a array of x values for
            x_values = np.linspace(x0, x1, int((x1 - x0) / 1) + 1)

            clothoid_func = lambda x: self.approx_clothoid([hA, c0, c1, dy], x)
            vfunc = np.vectorize(clothoid_func)
            y_values = vfunc(x_values)

            # for visualization in vehicle coordinates we need to rotate the values
            return -y_values, x_values
        else:
            return [], []
