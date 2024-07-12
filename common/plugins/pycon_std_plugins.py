from common.plugins.pycon_plugin_base import PyConPluginBase


class PyConStdPlugins:
    def __init__(self) -> None:
        self.plugin_control_panel: PyConPluginBase = None
        self.plugin_signal_explorer: PyConPluginBase = None
