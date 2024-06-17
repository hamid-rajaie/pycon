from enum import Enum

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

    class PyConLine:

        class PyConClothoid:

            def __init__(
                self,
                latDeviation=None,
                curvature=None,
                curvatureChange=None,
                headingAngle=None,
                startPositionX=None,
                lookAheadDistance=None,
            ) -> None:
                self.latDeviation = latDeviation
                self.curvature = curvature
                self.curvatureChange = curvatureChange
                self.headingAngle = headingAngle
                self.startPositionX = startPositionX
                self.lookAheadDistance = lookAheadDistance

        class PyConLineType(Enum):
            LEFT = "left"
            RIGHT = "right"
            LEFT_LEFT = "leftLeft"
            RIGHT_RIGHT = "rightRight"
            ROAD_EDGE_LEFT = "roadEdgeLeft"
            ROAD_EDGE_RIGHT = "roadEdgeRight"

        def __init__(self, line_type: PyConLineType, line_color: str, line_init_x: float, line_index: int) -> None:
            self.line_type = line_type
            self.line_color = line_color
            self.line_clothoid = PyConTopViewClothoid.PyConLine.PyConClothoid()
            self.line_x_array: np.ndarray = np.array([line_init_x for e in range(0, 100, 1)])
            self.line_y_array: np.ndarray = np.arange(0, 100, 1, dtype=float)
            self.line_index = line_index

    def __init__(self, params: PyConTopViewParams):
        super().__init__(name="PyConTopViewClothoid")

        self.pycon_data_source = params.pycon_data_source

        self.video_lines = [
            PyConTopViewClothoid.PyConLine(
                line_type=PyConTopViewClothoid.PyConLine.PyConLineType.LEFT.value,
                line_color="green",
                line_init_x=10,
                line_index=0,
            ),
            PyConTopViewClothoid.PyConLine(
                line_type=PyConTopViewClothoid.PyConLine.PyConLineType.RIGHT.value,
                line_color="green",
                line_init_x=-10,
                line_index=1,
            ),
            PyConTopViewClothoid.PyConLine(
                line_type=PyConTopViewClothoid.PyConLine.PyConLineType.LEFT_LEFT.value,
                line_color="blue",
                line_init_x=15,
                line_index=2,
            ),
            PyConTopViewClothoid.PyConLine(
                line_type=PyConTopViewClothoid.PyConLine.PyConLineType.RIGHT_RIGHT.value,
                line_color="blue",
                line_init_x=-15,
                line_index=3,
            ),
            PyConTopViewClothoid.PyConLine(
                line_type=PyConTopViewClothoid.PyConLine.PyConLineType.ROAD_EDGE_LEFT.value,
                line_color="red",
                line_init_x=20,
                line_index=4,
            ),
            PyConTopViewClothoid.PyConLine(
                line_type=PyConTopViewClothoid.PyConLine.PyConLineType.ROAD_EDGE_RIGHT.value,
                line_color="red",
                line_init_x=-20,
                line_index=5,
            ),
        ]

    def init_data(self):
        try:
            self.time = self.pycon_data_source.get_channel(channel_name="timestamp")

            for line in self.video_lines:
                line_type = line.line_type
                line_clothoid = line.line_clothoid

                latDeviation = f"videoLines.{line_type}.clothoid.latDeviation"
                curvature = f"videoLines.{line_type}.clothoid.curvature"
                curvatureChange = f"videoLines.{line_type}.clothoid.curvatureChange"
                headingAngle = f"videoLines.{line_type}.clothoid.headingAngle"
                startPositionX = f"videoLines.{line_type}.startPositionX"
                lookAheadDistance = f"videoLines.{line_type}.lookAheadDistance"

                line_clothoid.latDeviation = self.pycon_data_source.get_channel(channel_name=latDeviation)
                line_clothoid.curvature = self.pycon_data_source.get_channel(channel_name=curvature)
                line_clothoid.curvatureChange = self.pycon_data_source.get_channel(channel_name=curvatureChange)
                line_clothoid.headingAngle = self.pycon_data_source.get_channel(channel_name=headingAngle)
                line_clothoid.startPositionX = self.pycon_data_source.get_channel(channel_name=startPositionX)
                line_clothoid.lookAheadDistance = self.pycon_data_source.get_channel(channel_name=lookAheadDistance)

            self.set_status_ok()

        except Exception as ex:
            logger().warning(str(ex))

    def init(self, ax: axes, lines_2d: list):
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.html#matplotlib.axes.Axes
        #
        # https://matplotlib.org/stable/api/axes_api.html

        for line in self.video_lines:

            line_2d_list = self.plot_data(
                ax=ax,
                x_array=line.line_x_array,
                y_array=line.line_y_array,
                # marker="o",
                color=line.line_color,
                linewidth=0.5,
                markersize=2,
                label="left",
            )

            lines_2d.append(line_2d_list[0])

    def render(self, time_sec, lines_2d: list):

        if self.is_status_not_ok():
            return

        idx, t = find_nearest_time(arr=self.time.samples, value=time_sec)

        for line in self.video_lines:

            x_array, y_array = self.provide_clothoid_values(
                latDeviation=line.line_clothoid.latDeviation.samples[idx],
                curvature=line.line_clothoid.curvature.samples[idx],
                curvatureChange=line.line_clothoid.curvatureChange.samples[idx],
                headingAngle=line.line_clothoid.headingAngle.samples[idx],
                startPositionX=line.line_clothoid.startPositionX.samples[idx],
                lookAheadDistance=line.line_clothoid.lookAheadDistance.samples[idx],
            )

            lines_2d[line.line_index].set_xdata(x_array)
            lines_2d[line.line_index].set_ydata(y_array)
            lines_2d[line.line_index].set_color(line.line_color)

    def provide_clothoid_values(
        self,
        latDeviation: float,
        curvature: float,
        curvatureChange: float,
        headingAngle: float,
        startPositionX: float,
        lookAheadDistance: float,
    ) -> tuple[np.ndarray, np.ndarray]:

        dy = latDeviation
        c0 = curvature
        c1 = curvatureChange
        hA = headingAngle
        x0 = startPositionX
        x1 = lookAheadDistance

        if x1 - x0 > 0:

            x_values = np.linspace(x0, x1, int((x1 - x0) / 1) + 1)

            clothoid_func = lambda x: self.approx_clothoid([hA, c0, c1, dy], x)
            vfunc = np.vectorize(clothoid_func)
            y_values = vfunc(x_values)

            return -y_values, x_values
        else:
            return [], []

    def approx_clothoid(self, clothoid, x):

        x_cs = x / np.cos(clothoid[0])
        L = x_cs + 1 / 6 * x_cs**3 * clothoid[1] ** 2
        y_cs = L**2 * (1 / 2 * clothoid[1] + 1 / 6 * clothoid[2] * L)
        y = np.sin(clothoid[0]) * x_cs + np.cos(clothoid[0]) * y_cs + clothoid[3]

        return y
