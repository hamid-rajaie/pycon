import importlib
import os

from PyQt5.QtCore import QSettings

from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from common.plugins.pycon_std_plugins import PyConStdPlugins
from plugins_std.pycon_plugin_control_panel import PyConPluginControlPanel
from plugins_std.pycon_plugin_signal_explorer import PyConPluginSignalExplorer
from pycon_config import get_pycon_config


class PyConPlugins:

    def __init__(self, plugin_params: PyConPluginParams):
        self.plugin_params = plugin_params
        self.std_plugins = PyConStdPlugins()
        #
        # {'plugin_menu_group_1' : [] , 'plugin_menu_group_2' : [] }
        #
        self.detected_plugins = {}

        self.__create_std_plugin()
        self.__discover_plugins()

    def initPlugins(self):
        for _, plugin in self.std_plugins.__dict__.items():
            plugin.initPlugin()

        for plugin_menu_group, list_plugins in self.detected_plugins.items():
            for plugin in list_plugins:
                plugin.initPlugin()

    def add_generic_signals(self):
        for _, plugin in self.std_plugins.__dict__.items():
            plugin.add_generic_signals()

        for plugin_menu_group, list_plugins in self.detected_plugins.items():
            for plugin in list_plugins:
                plugin.add_generic_signals()

    def connect(self):
        # ==================================================
        # connect plugin_signal_explorer to plugin_control_panel
        # ==================================================
        self.std_plugins.plugin_signal_explorer.signal_explorer_double_click.connect(
            self.std_plugins.plugin_control_panel.slot_add_signal_by_double_click
        )
        # ==================================================================
        # add connections
        # connect std panels to self
        # ==================================================================
        for plugin_menu_group, list_plugins in self.detected_plugins.items():
            for plugin in list_plugins:
                if isinstance(plugin, PyConPluginBase):
                    # ==================================================================
                    # connect : plugin_signal_explorer   signal_explorer_double_click
                    # to      : plugin                slot_add_signal_by_double_click
                    # ==================================================================
                    self.std_plugins.plugin_signal_explorer.signal_explorer_double_click.connect(
                        plugin.slot_add_signal_by_double_click
                    )
                    # ==================================================================
                    # connect : plugin_control_panel   control_panel_slider_value_changed
                    # to      : plugin              slider_value_changed
                    # ==================================================================
                    self.std_plugins.plugin_control_panel.control_panel_slider_value_changed.connect(
                        plugin.slider_value_changed
                    )

    def save_settings(self, settings: QSettings):
        # ==================================================================
        # save plugin settings
        # ==================================================================
        def local_save(plugin):
            settings.beginGroup(plugin.windowTitle())
            settings.setValue("visible", plugin.isVisible())
            settings.setValue("geometry", plugin.geometry())
            for key, val in plugin.get_settings().items():
                settings.setValue(key, val)
            settings.endGroup()

        for _, plugin in self.std_plugins.__dict__.items():
            if isinstance(plugin, PyConPluginBase):
                local_save(plugin)

        for plugin_menu_group, list_plugins in self.detected_plugins.items():
            for plugin in list_plugins:
                if isinstance(plugin, PyConPluginBase):
                    local_save(plugin)

    def __create_std_plugin(self):
        self.std_plugins.plugin_control_panel = PyConPluginControlPanel()
        self.std_plugins.plugin_signal_explorer = PyConPluginSignalExplorer(params=self.plugin_params)

    def __discover_plugins(self):

        for plugin_cfg in get_pycon_config().pycon_plugins_cfg:
            plugin_package = plugin_cfg["plugin_package"]
            plugin_dir = plugin_cfg["plugin_dir"]
            plugin_menu_group = plugin_cfg["plugin_menu_group"]

            if plugin_menu_group not in self.detected_plugins.keys():
                self.detected_plugins[plugin_menu_group] = []

            if os.path.isdir(plugin_dir):
                for file_name in os.listdir(plugin_dir):
                    if file_name.endswith(".py") and file_name != "__init__.py":
                        module_name = file_name[:-3]
                        module = importlib.import_module(name=f".{module_name}", package=plugin_package)
                        for item_name in dir(module):
                            item = getattr(module, item_name)
                            if (
                                (isinstance(item, type))
                                and issubclass(item, PyConPluginBase)
                                and item != PyConPluginBase
                            ):
                                _plg = item(self.plugin_params)
                                self.detected_plugins[plugin_menu_group].append(_plg)
