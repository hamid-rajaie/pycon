import matplotlib.axes as axes
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMdiSubWindow

from common.logging.logger import logger
from common.pycon_numpy import find_nearest_time
from plugins.top_view.plugins.common.pycon_top_view_params import PyConTopViewParams
from plugins.top_view.plugins.common.pycon_top_view_plugin_base import PyConTopViewPluginBase


class PyConTopViewClothoid(PyConTopViewPluginBase):

    def __init__(self, params: PyConTopViewParams):
        super().__init__(name="PyConTopViewClothoid")

        self.pycon_app_data_source = params.pycon_app_data_source

    def load_signals(self):
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

    def init(self, ax: axes, plot_lines: list):
        # https://matplotlib.org/stable/api/axes_api.html
        x_array = np.arange(-50, 50, 1, dtype=float)
        y_array = np.arange(0, 100, 1, dtype=float)

        lines = self.plot_data(
            ax=ax, x=x_array, y=y_array, marker="o", color="blue", linewidth=0.5, markersize=2, label="left"
        )
        logger().info(f"type of plot_data ret : {type(lines)}, len : {len(lines)}")

        plot_lines.append(lines[0])

    def draw(self, time_sec, plot_lines: list):

        idx, t = find_nearest_time(arr=self.time.samples, value=time_sec)

        latDeviation = self.latDeviation.samples[idx]
        curvature = self.curvature.samples[idx]
        curvatureChange = self.curvatureChange.samples[idx]
        headingAngle = self.headingAngle.samples[idx]
        startPositionX = self.startPositionX.samples[idx]
        lookAheadDistance = self.lookAheadDistance.samples[idx]

        x_array, y_array = self.provide_clothoid_values(
            latDeviation=latDeviation,
            curvature=curvature,
            curvatureChange=curvatureChange,
            headingAngle=headingAngle,
            startPositionX=startPositionX,
            lookAheadDistance=lookAheadDistance,
        )
        line_index = 0

        plot_lines[line_index].set_xdata(x_array)
        plot_lines[line_index].set_ydata(y_array)
        plot_lines[line_index].set_color("blue")

        # ax = self.plot_lines[0][0].axes
        # title = f"GT Plot idx: {val} [{self.df.iloc[int(val)]['timestamp']}s]"
        # if self.adma_available:
        #    title += f"\nLocation: ({round(self.df.iloc[int(val)]['lat_wgs84'], 5)}|{round(self.df.iloc[int(val)]['lon_wgs84'],5)})"
        # ax.set_title(title)

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
