import importlib
import os

from PyQt5 import uic
from PyQt5.QtCore import QRect, QSettings
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QMainWindow,
    QMdiArea,
    QMdiSubWindow,
    QMenu,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from common.pycon_std_panels import PyConStdPanels
from data_sources.pycon_data_source_csv import PyConDataSourceCsv
from data_sources.pycon_data_source_mdf import PyConDataSourceMdf
from main_window.pycon_main_window_dialog_about import PyConAboutDialog
from plugins_std.pycon_window_control_panel import PyConWindowControlPanel
from plugins_std.pycon_window_signal_explorer import PyConWindowSignalExplorer
from pycon_config import get_pycon_config


class PyConMainWindow(QMainWindow):
    def __init__(self):
        super(PyConMainWindow, self).__init__()

        uic.loadUi("main_window/pycon_main_window.ui", self)

        self.open_dir = None

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

        if get_pycon_config().pycon_bg_color is not None:
            self.setStyleSheet(f"background-color: {get_pycon_config().pycon_bg_color};")
        #
        # add tab widget
        #
        self.tab_widget = QTabWidget()
        if get_pycon_config().pycon_bg_color_tabs is not None:
            self.tab_widget.setStyleSheet(f"background-color: {get_pycon_config().pycon_bg_color_tabs};")
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(lambda index: self.tab_widget.removeTab(index))
        self.setCentralWidget(self.tab_widget)
        #
        # add menu
        #
        self.create_menu_bar()

        self.show()

    def closeEvent(self, e):

        self.settings.beginGroup("config")
        self.settings.setValue("open_dir", self.open_dir)
        self.settings.endGroup()

        self.settings.beginGroup("PyConMainWindow")
        self.settings.setValue("geometry", self.geometry())
        self.settings.endGroup()

        tab = self.tab_widget.currentWidget()

        if tab is not None and tab.std_plugins is not None:
            std_plugins: PyConStdPanels = tab.std_plugins

            for _, obj in std_plugins.__dict__.items():
                if isinstance(obj, QMdiSubWindow):
                    self.settings.beginGroup(obj.windowTitle())
                    self.settings.setValue("visible", obj.isVisible())
                    self.settings.setValue("geometry", obj.geometry())
                    self.settings.endGroup()

        if tab is not None and tab.plugins is not None:
            plugins = tab.plugins

            for plugin in plugins:
                if isinstance(plugin, QMdiSubWindow):
                    self.settings.beginGroup(plugin.windowTitle())
                    self.settings.setValue("visible", plugin.isVisible())
                    self.settings.setValue("geometry", plugin.geometry())
                    self.settings.endGroup()

    def create_menu_bar(self):
        action_open = QAction("Open...", self)
        action_exit = QAction("Exit", self)
        action_about = QAction("About", self)

        action_open.triggered.connect(self.open_file)
        action_about.triggered.connect(self.about)

        menu_bar = self.menuBar()

        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)
        file_menu.addAction(action_open)

        file_menu.addSeparator()
        file_menu.addAction(action_exit)

        file_wins = QMenu("&Windows", self)
        menu_bar.addMenu(file_wins)

        help_menu = menu_bar.addMenu("&Help")
        help_menu.addAction(action_about)

        self.file_wins = file_wins

    def about(self):
        dialog = PyConAboutDialog()
        dialog.exec_()

    def discover_plugins(self, params: PyConPluginParams):
        plugins = []

        for plugin_cfg in get_pycon_config().pycon_plugins_cfg:
            plugin_package = plugin_cfg["plugin_package"]
            plugin_dir = plugin_cfg["plugin_dir"]

            if os.path.isdir(plugin_dir):
                for file_name in os.listdir(plugin_dir):
                    if file_name.endswith(".py") and file_name != "__init__.py":
                        module_name = file_name[:-3]
                        module = importlib.import_module(name=f".{module_name}", package=plugin_package)
                        for item_name in dir(module):
                            # logger().info(f"... item_name:{item_name}")
                            item = getattr(module, item_name)
                            if (
                                (isinstance(item, type))
                                and issubclass(item, PyConPluginBase)
                                and item != PyConPluginBase
                            ):
                                plugins.append(item(params))

        return plugins

    def init_plugin(self, tab_mdi_area, obj):
        if isinstance(obj, QMdiSubWindow):
            self.settings.beginGroup(obj.windowTitle())
            visible: bool = self.settings.value("visible", False, type=bool)
            geometry: QRect = self.settings.value("geometry", QRect(0, 0, 400, 400))

            obj.setGeometry(geometry)

            if get_pycon_config().pycon_bg_color_tab_sub_win is not None:
                obj.setStyleSheet(f"background-color: {get_pycon_config().pycon_bg_color_tab_sub_win};")

            tab_mdi_area.addSubWindow(obj)

            def lambda_generator(obj):
                return lambda: obj.show()

            action = QAction(obj.windowTitle(), self)
            action.triggered.connect(lambda_generator(obj))
            self.file_wins.addAction(action)

            if visible:
                obj.show()
            else:
                obj.hide()

            self.settings.endGroup()

    def open_file(self):
        self.settings.beginGroup("config")
        _dir: str = self.settings.value("open_dir", "")
        self.settings.endGroup()

        logger().info(f"open dir : {_dir}")

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
            if file_basename_ext == ".csv":
                pycon_app_data_source = PyConDataSourceCsv(file_name=selected_file_name)

            if file_basename_ext in [".mf4", ".MF4"]:
                pycon_app_data_source = PyConDataSourceMdf(file_name=selected_file_name)
            # ==================================================
            # add tab
            # ==================================================
            tab_mdi_area = QMdiArea()
            # tab_mdi_area.setBackground(get_pycon_config().pycon_bg_color_tab_mdi)
            tab = QWidget()
            if get_pycon_config().pycon_bg_color_tab is not None:
                tab.setStyleSheet(f"background-color: {get_pycon_config().pycon_bg_color_tab};")
            self.tab_widget.addTab(tab, file_basename)
            self.tab_widget.setCurrentWidget(tab)

            tab_layout = QVBoxLayout()
            tab_layout.addWidget(tab_mdi_area)
            tab.setLayout(tab_layout)

            tab_mdi_area.setGeometry(tab.geometry())
            # ==================================================================
            # create params
            # ==================================================================
            panel_params = PyConPluginParams(
                selected_file_name=selected_file_name,
                tab=tab,
                tab_mdi_area=tab_mdi_area,
                pycon_app_data_source=pycon_app_data_source,
            )
            # ==================================================================
            # create std_plugins
            # ==================================================================
            std_plugins = PyConStdPanels()
            tab.std_plugins = std_plugins

            std_plugins.win_control_panel = PyConWindowControlPanel()
            std_plugins.win_signal_explorer = PyConWindowSignalExplorer(
                pycon_app_data_source=panel_params.pycon_app_data_source
            )
            # ==================================================================
            # detect plugins
            # ==================================================================
            plugins = self.discover_plugins(params=panel_params)
            tab.plugins = plugins
            # ==================================================================
            # init plugins
            # ==================================================================
            for _, obj in std_plugins.__dict__.items():
                self.init_plugin(tab_mdi_area=tab_mdi_area, obj=obj)

            for plugin in plugins:
                self.init_plugin(tab_mdi_area=tab_mdi_area, obj=plugin)
            # ==================================================
            # connect win_signal_explorer to win_control_panel
            # ==================================================
            std_plugins.win_signal_explorer.signal_explorer_double_click.connect(
                std_plugins.win_control_panel.slot_add_signal_by_double_click
            )
            # ==================================================================
            # add connections
            # connect std panels to plugins
            # ==================================================================
            for plugin in plugins:
                if isinstance(plugin, QMdiSubWindow):

                    def lambda_generator(plugin):
                        return obj.slot_add_signal_by_double_click

                    # ==================================================================
                    # connect : win_signal_explorer   signal_explorer_double_click
                    # to      : plugin                slot_add_signal_by_double_click
                    # ==================================================================
                    std_plugins.win_signal_explorer.signal_explorer_double_click.connect(
                        plugin.slot_add_signal_by_double_click
                    )
                    # ==================================================================
                    # connect : win_control_panel   control_panel_slider_value_changed
                    # to      : plugin              slider_value_changed
                    # ==================================================================
                    std_plugins.win_control_panel.control_panel_slider_value_changed.connect(
                        plugin.slider_value_changed
                    )
