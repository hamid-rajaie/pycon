import logging
import os
from threading import Lock
from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush


class PyConConfig:
    def __init__(self) -> None:
        # ======================================================================
        # logging
        # ======================================================================
        self.log_file: str = "C:\\develop\pycon\\pycon.log"

        self.verbose_logging: Union[dict[str, bool], None] = {"log_process": False, "log_thread": False}
        self.logging_handlers: list[str] = ["terminal", "file"]
        self.delete_old_log_at_startup: bool = True
        self.log_api_prefix: bool = False
        self.pycon_log_level: int = logging.INFO
        # ======================================================================
        #
        # ======================================================================

        self.pycon_start_dir_filter = ["CSV Files (*.csv)", "CanAPE (*.mf4)"]
        self.pycon_start_dir_filter_selected = self.pycon_start_dir_filter[0]

        self.pycon_bg_color = None  # "black"
        self.pycon_bg_color_tabs = None  # "lightgrey"
        self.pycon_bg_color_tab = None  # "lightgrey"
        self.pycon_bg_color_tab_mdi = None  # QBrush(Qt.white)
        self.pycon_bg_color_tab_sub_win = None  # "lightgrey"

        # convert sec to msec
        self.pycon_conversion_factor__time = 1000

        self.pycon_plugins_cfg = [
            {
                "plugin_package": "plugins",
                "plugin_dir": "C:\\develop\\pycon\\plugins",
            },
            {
                "plugin_package": "plugins.templates",
                "plugin_dir": "C:\\develop\\pycon\\plugins\\templates",
            },
            {
                "plugin_package": "plugins.videos",
                "plugin_dir": "C:\\develop\\pycon\\plugins\\videos",
            },
            {
                "plugin_package": "plugins.tables",
                "plugin_dir": "C:\\develop\\pycon\\plugins\\tables",
            },
            {
                "plugin_package": "plugins.plots",
                "plugin_dir": "C:\\develop\\pycon\\plugins\\plots",
            },
            {
                "plugin_package": "plugins.geo_maps",
                "plugin_dir": "C:\\develop\\pycon\\plugins\\geo_maps",
            },
        ]


g_pycon_config = None
g_pycon_config_watchdog = None
g_pycon_config_lock = Lock()


def get_pycon_config():
    global g_pycon_config
    global g_pycon_config_lock

    with g_pycon_config_lock:
        if g_pycon_config is None:
            g_pycon_config = PyConConfig()

    return g_pycon_config
