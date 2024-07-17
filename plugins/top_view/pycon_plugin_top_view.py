import importlib
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QGridLayout, QMenu, QWidget

from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from plugins.top_view.common.pycon_top_view_params import PyConTopViewParams
from plugins.top_view.common.pycon_top_view_plugin_base import PyConTopViewPluginBase
from plugins_std.pycon_time import PyConTime
from pycon_config import get_pycon_config


class PyConWindowTopView(PyConPluginBase):

    def __init__(self, params: PyConPluginParams):
        super().__init__()

        self.setWindowTitle("Top View")
        self.resize(500, 700)

        self.pycon_data_source = params.pycon_data_source

        self.plugins = None
        self.lines_2d = []
        self.widget_1_layout = None

        self.set_status_not_ok()

        self.__initUI()

        # ======================================================================
        # create params
        # ======================================================================
        top_view_params = PyConTopViewParams(pycon_data_source=self.pycon_data_source)

        self.plugins = self.__discover_plugins(params=top_view_params)

        for plugin in self.plugins:
            logger().info(f"found top view plugin : {plugin.name}")

        self.__create_top_view()

    def __initUI(self):
        widget = QWidget()
        self.widget_1_layout = QGridLayout(widget)

        pal = widget.palette()
        widget.setAutoFillBackground(True)
        pal.setColor(widget.backgroundRole(), Qt.white)
        widget.setPalette(pal)

        super().initUI(widget=widget, with_menubar=True)

    def add_generic_signals(self):
        if self.is_status_ok():
            for plugin in self.plugins:
                plugin.add_generic_signals()

    def initPlugin(self):
        if self.is_status_ok():
            for plugin in self.plugins:
                plugin.initPlugin()

    def get_settings(self):
        for plugin in self.plugins:
            self.settings[plugin.name] = {}
        return self.settings

    def __discover_plugins(self, params: PyConTopViewParams):
        plugins = []

        for plugin_cfg in get_pycon_config().pycon_plugins_top_view_cfg:
            plugin_package = plugin_cfg["plugin_package"]
            plugin_dir = plugin_cfg["plugin_dir"]

            if os.path.isdir(plugin_dir):
                for file_name in os.listdir(plugin_dir):
                    if file_name.endswith(".py") and file_name != "__init__.py":
                        module_name = file_name[:-3]
                        module = importlib.import_module(name=f".{module_name}", package=plugin_package)
                        for item_name in dir(module):
                            item = getattr(module, item_name)
                            if (
                                (isinstance(item, type))
                                and issubclass(item, PyConTopViewPluginBase)
                                and item != PyConTopViewPluginBase
                            ):
                                plugins.append(item(params))

        return plugins

    def __create_top_view(self):
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figurex
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.html#matplotlib.axes.Axes
        #
        # https://matplotlib.org/stable/api/figure_api.html
        # https://matplotlib.org/stable/api/axes_api.html
        fig, ax = plt.subplots()
        # fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

        for plugin in self.plugins:
            plugin.init(ax, self.lines_2d)

        self.canvas = FigureCanvas(fig)
        self.nav_toolbar = NavigationToolbar(self.canvas, self)
        self.widget_1_layout.addWidget(self.nav_toolbar)
        self.widget_1_layout.addWidget(self.canvas)
        self.canvas.draw()

    @QtCore.pyqtSlot(PyConTime)
    def slider_value_changed(self, time: PyConTime):

        time_sec = time.get_time_sec()

        for plugin in self.plugins:
            plugin.render(time_sec, self.lines_2d)

        self.canvas.draw()
