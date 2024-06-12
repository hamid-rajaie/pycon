from PyQt5 import uic

from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams


class PyConWindowPlugin_2(PyConPluginBase):

    def __init__(self, params: PyConPluginParams):
        super().__init__()

        uic.loadUiType("plugins/templates/pycon_window_plugin_2.ui", self)
        self.setWindowTitle("Plugin 2")

        self.win_widget = None
        self.video_label = None
        self.video_time_msec = 0
        self.cap = None

        self.__initUI()

    def __initUI(self):
        pass
