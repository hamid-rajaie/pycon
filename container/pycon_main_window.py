import importlib
import os

from PyQt5.QtCore import QRect, QSettings
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFileDialog,
    QMainWindow,
    QMdiArea,
    QMdiSubWindow,
    QMenu,
    QMessageBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from common.pycon_std_plugins import PyConStdPlugins
from container.pycon_dialog_wait import PyConDialogWait
from container.pycon_main_window_dialog_about import PyConAboutDialog
from data_sources.pycon_data_source_csv import PyConDataSourceCsv
from data_sources.pycon_data_source_mdf import PyConDataSourceMdf
from plugins_std.pycon_plugin_control_panel import PyConPluginControlPanel
from plugins_std.pycon_plugin_signal_explorer import PyConPluginSignalExplorer
from pycon_config import get_pycon_config


class PyConMainWindow(QMainWindow):
    def __init__(self):
        super(PyConMainWindow, self).__init__()

        self.open_dir = None

        self.menu_groups = {}
        # ======================================================================
        # app setting
        # ======================================================================
        settings_file_path = "pycon_settings.ini"
        self.settings = QSettings(settings_file_path, QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)
        # ======================================================================
        # read settings
        # ======================================================================
        self.settings.beginGroup("PyConMainWindow")
        main_window_geometry: QRect = self.settings.value("geometry", QRect(0, 0, 1800, 800))
        self.settings.endGroup()

        self.setWindowTitle("PyCon")
        self.setGeometry(main_window_geometry)
        #
        # add tab widget
        #
        self.tab_widget = QTabWidget()

        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(lambda index: self.tab_widget.removeTab(index))
        self.setCentralWidget(self.tab_widget)
        #
        # add menu
        #
        self.__create_menu_bar()

        self.show()

    def closeEvent(self, e):

        self.settings.beginGroup("config")
        self.settings.setValue("open_dir", self.open_dir)
        self.settings.endGroup()

        self.settings.beginGroup("PyConMainWindow")
        self.settings.setValue("geometry", self.geometry())
        self.settings.endGroup()

        tab = self.tab_widget.currentWidget()
        # ==================================================================
        # save settings : std plugins
        # ==================================================================
        if tab is not None and tab.std_plugins is not None:
            std_plugins: PyConStdPlugins = tab.std_plugins

            for _, plugin in std_plugins.__dict__.items():
                if isinstance(plugin, QMdiSubWindow):
                    self.settings.beginGroup(plugin.windowTitle())
                    self.settings.setValue("visible", plugin.isVisible())
                    self.settings.setValue("geometry", plugin.geometry())
                    self.settings.endGroup()
        # ==================================================================
        # save settings : plugins
        # ==================================================================
        if tab is not None and tab.plugins is not None:
            for plugin_menu_group, list_plugins in tab.plugins.items():
                for plugin in list_plugins:
                    if isinstance(plugin, QMdiSubWindow):
                        self.settings.beginGroup(plugin.windowTitle())
                        self.settings.setValue("visible", plugin.isVisible())
                        self.settings.setValue("geometry", plugin.geometry())
                        self.settings.endGroup()

    def __create_menu_bar(self):
        action_open = QAction("Open...", self)
        action_exit = QAction("Exit", self)
        action_about = QAction("About", self)

        action_open.triggered.connect(self.open_file)
        action_about.triggered.connect(self.about)

        menu_bar = self.menuBar()

        menu_file = QMenu("&File", self)
        menu_bar.addMenu(menu_file)
        menu_file.addAction(action_open)

        menu_file.addSeparator()
        menu_file.addAction(action_exit)

        menu_plugins = QMenu("&Plugins", self)
        menu_bar.addMenu(menu_plugins)

        menu_help = menu_bar.addMenu("&Help")
        menu_help.addAction(action_about)

        self.menu_plugins = menu_plugins

    def about(self):
        dialog = PyConAboutDialog()
        dialog.exec_()

    def __discover_plugins(self, params: PyConPluginParams):
        detected_plugins = {}

        for plugin_cfg in get_pycon_config().pycon_plugins_cfg:
            plugin_package = plugin_cfg["plugin_package"]
            plugin_dir = plugin_cfg["plugin_dir"]
            plugin_menu_group = plugin_cfg["plugin_menu_group"]

            if plugin_menu_group not in self.menu_groups.keys():
                detected_plugins[plugin_menu_group] = []

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
                                detected_plugins[plugin_menu_group].append(item(params))

        return detected_plugins

    def __setup_plugin_geometry(self, tab_mdi_area, plugin, parent_menu):
        if isinstance(plugin, QMdiSubWindow):
            self.settings.beginGroup(plugin.windowTitle())
            visible: bool = self.settings.value("visible", False, type=bool)
            geometry: QRect = self.settings.value("geometry", QRect(0, 0, 400, 400))

            plugin.setGeometry(geometry)

            tab_mdi_area.addSubWindow(plugin)

            def lambda_generator(plugin):
                return lambda: plugin.show()

            action = QAction(plugin.windowTitle(), self)
            action.triggered.connect(lambda_generator(plugin))

            parent_menu.addAction(action)

            if visible:
                plugin.show()
            else:
                plugin.hide()

            self.settings.endGroup()

    def open_file(self):
        self.settings.beginGroup("config")
        _dir: str = self.settings.value("open_dir", "")
        self.settings.endGroup()

        dlg = QFileDialog(directory=_dir)

        dlg.setNameFilters(get_pycon_config().pycon_start_dir_filter)
        dlg.selectNameFilter(get_pycon_config().pycon_start_dir_filter_selected)

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            selected_file_name = filenames[0]
            file_basename = os.path.basename(selected_file_name)
            self.open_dir = os.path.dirname(selected_file_name)
            file_basename_no_ext, file_basename_ext = os.path.splitext(file_basename)

            # ==================================================
            # Data Source
            # ==================================================
            dlg_wait = PyConDialogWait(self, "Loading File")
            if file_basename_ext == ".csv":
                pycon_data_source = PyConDataSourceCsv(file_name=selected_file_name)

            if file_basename_ext in [".mf4", ".MF4"]:
                pycon_data_source = PyConDataSourceMdf(file_name=selected_file_name)
            dlg_wait.hide_dialog()
            # ==================================================
            # add tab
            # ==================================================
            tab_mdi_area = QMdiArea()

            tab = QWidget()

            self.tab_widget.addTab(tab, file_basename)
            self.tab_widget.setCurrentWidget(tab)

            tab_layout = QVBoxLayout()
            tab_layout.addWidget(tab_mdi_area)
            tab.setLayout(tab_layout)

            tab_mdi_area.setGeometry(tab.geometry())
            # ==================================================================
            # create params
            # ==================================================================
            plugin_params = PyConPluginParams(
                selected_file_name=selected_file_name, pycon_data_source=pycon_data_source, settings=self.settings
            )
            if True:
                # ==================================================================
                # create std_plugins
                #
                # dlg_wait = PyConDialogWait(self, "Loading Plugins")
                std_plugins = PyConStdPlugins()
                tab.std_plugins = std_plugins

                std_plugins.plugin_control_panel = PyConPluginControlPanel()
                std_plugins.plugin_signal_explorer = PyConPluginSignalExplorer(
                    pycon_data_source=plugin_params.pycon_data_source
                )
                #
                # detect plugins
                #
                tab.plugins = self.__discover_plugins(params=plugin_params)
                # dlg_wait.hide_dialog()

            if True:
                # ==================================================================
                # init std plugins geoms
                #
                # dlg_wait = PyConDialogWait(self, "Initializing Plugin Geometries")
                menu_grp = QMenu("&Standard", self)
                self.menu_plugins.addMenu(menu_grp)
                self.menu_groups["std"] = menu_grp
                for _, plugin in std_plugins.__dict__.items():
                    self.__setup_plugin_geometry(tab_mdi_area=tab_mdi_area, plugin=plugin, parent_menu=menu_grp)
                #
                # init tab.plugins geoms
                #
                for plugin_menu_group, list_plugins in tab.plugins.items():
                    menu_grp = QMenu(plugin_menu_group, self)
                    self.menu_plugins.addMenu(menu_grp)
                    self.menu_groups[plugin_menu_group] = menu_grp

                    for plugin in list_plugins:
                        self.__setup_plugin_geometry(tab_mdi_area=tab_mdi_area, plugin=plugin, parent_menu=menu_grp)
                # dlg_wait.hide_dialog()

            if True:
                dlg_wait = PyConDialogWait(self, "Initializing Plugin Data")
                # ==================================================================
                # init data std tab.plugins
                #
                for _, plugin in std_plugins.__dict__.items():
                    plugin.init_data()
                #
                # init data tab.plugins
                #
                for plugin_menu_group, list_plugins in tab.plugins.items():
                    for plugin in list_plugins:
                        plugin.init_data()
                dlg_wait.hide_dialog()
            # ==================================================
            # connect plugin_signal_explorer to plugin_control_panel
            # ==================================================
            std_plugins.plugin_signal_explorer.signal_explorer_double_click.connect(
                std_plugins.plugin_control_panel.slot_add_signal_by_double_click
            )
            # ==================================================================
            # add connections
            # connect std panels to tab.plugins
            # ==================================================================
            for plugin_menu_group, list_plugins in tab.plugins.items():
                for plugin in list_plugins:
                    if isinstance(plugin, QMdiSubWindow):

                        # def lambda_generator(plugin):
                        #    return plugin.slot_add_signal_by_double_click

                        # ==================================================================
                        # connect : plugin_signal_explorer   signal_explorer_double_click
                        # to      : plugin                slot_add_signal_by_double_click
                        # ==================================================================
                        std_plugins.plugin_signal_explorer.signal_explorer_double_click.connect(
                            plugin.slot_add_signal_by_double_click
                        )
                        # ==================================================================
                        # connect : plugin_control_panel   control_panel_slider_value_changed
                        # to      : plugin              slider_value_changed
                        # ==================================================================
                        std_plugins.plugin_control_panel.control_panel_slider_value_changed.connect(
                            plugin.slider_value_changed
                        )
