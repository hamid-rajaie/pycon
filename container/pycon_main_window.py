import os

from PyQt5.QtCore import QRect, QSettings
from PyQt5.QtWidgets import QAction, QFileDialog, QMainWindow, QMdiArea, QMenu, QTabWidget, QVBoxLayout, QWidget

from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from common.plugins.pycon_plugins import PyConPlugins
from container.pycon_dialog_wait import PyConDialogWait
from container.pycon_main_window_dialog_about import PyConAboutDialog
from data_sources.pycon_data_source_csv import PyConDataSourceCsv
from data_sources.pycon_data_source_mdf import PyConDataSourceMdf
from pycon_config import get_pycon_config


class PyConMainWindow(QMainWindow):
    def __init__(self):
        super(PyConMainWindow, self).__init__()

        self.open_dir = None

        self.menu_created = False
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
        self.save_settings()

    def save_settings(self):

        self.settings.beginGroup("config")
        self.settings.setValue("open_dir", self.open_dir)
        self.settings.endGroup()

        self.settings.beginGroup("PyConMainWindow")
        self.settings.setValue("geometry", self.geometry())
        self.settings.endGroup()

        tab = self.tab_widget.currentWidget()

        if tab is not None:
            tab.plugins.save_settings(settings=self.settings)

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
            # create data source
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
                selected_file_name=selected_file_name, pycon_data_source=pycon_data_source, initial_yaml_dir=_dir
            )
            tab.plugins = PyConPlugins(plugin_params=plugin_params)
            # ==================================================================
            # setup main menu
            # ==================================================================
            if not self.menu_created:
                menu_grp = QMenu("&Standard", self)
                self.menu_plugins.addMenu(menu_grp)

                for plugin_menu_group, list_plugins in tab.plugins.detected_plugins.items():
                    menu_grp = QMenu(plugin_menu_group, self)
                    self.menu_plugins.addMenu(menu_grp)

                    def lambda_generator(plugin):
                        return lambda: plugin.show()

                    for plugin in list_plugins:
                        action = QAction(plugin.windowTitle(), self)
                        action.triggered.connect(lambda_generator(plugin))

                        menu_grp.addAction(action)

                self.menu_created = True
            # ==================================================================
            # setup plugin geometries
            # ==================================================================
            for _, plugin in tab.plugins.std_plugins.__dict__.items():
                self.__setup_plugin_geometry(tab_mdi_area=tab_mdi_area, plugin=plugin)

            for plugin_menu_group, list_plugins in tab.plugins.detected_plugins.items():
                for plugin in list_plugins:
                    self.__setup_plugin_geometry(tab_mdi_area=tab_mdi_area, plugin=plugin)
            # ==============================================================
            # initialize  plugins
            # ==============================================================
            dlg_wait = PyConDialogWait(self, "Initializing Plugin Data")
            tab.plugins.get_needed_signals()
            tab.plugins.initialize()
            tab.plugins.connect()
            dlg_wait.hide_dialog()

    def __setup_plugin_geometry(self, tab_mdi_area, plugin):
        if isinstance(plugin, PyConPluginBase):
            self.settings.beginGroup(plugin.windowTitle())
            visible: bool = self.settings.value("visible", False, type=bool)
            geometry: QRect = self.settings.value("geometry", QRect(0, 0, 400, 400))

            plugin.setGeometry(geometry)

            tab_mdi_area.addSubWindow(plugin)

            if visible:
                plugin.show()
            else:
                plugin.hide()

            self.settings.endGroup()
