import os
import re

import numpy as np
import yaml
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (
    QFileDialog,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from common.delegates.pycon_window_signal_explorer_delegate import PyConWindowSignalExplorerDelegate
from common.generic_signals.pycon_generic_yaml import PyConGenericYaml
from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from data_sources.pycon_data_source import PyConDataSource
from data_sources.pycon_standard_item import PyConStandardItem
from pycon_config import get_pycon_config


class PyConWindowPlugin_2(PyConPluginBase):
    # ==================================================
    # SIGNALS
    # ==================================================
    signal_explorer_double_click = QtCore.pyqtSignal(int, int, str, np.ndarray, np.ndarray)

    def __init__(self, params: PyConPluginParams):
        super().__init__()

        self.pycon_data_source = params.pycon_data_source
        self.initial_yaml_dir = params.initial_yaml_dir

        self.generic_yaml = PyConGenericYaml(pycon_data_source=params.pycon_data_source)

        self.setWindowTitle("Plugin yaml")
        #
        # read csv
        #
        self.data_frame = None

        self.table_widget = None
        self.signal_tree_model = None
        self.signal_tree_view = None
        self.root_node = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.slot_timer_timeout)
        self.timer_started = False

        self.search_time_out = 1000

        self.search_text = ""
        self.search_cnt = 0

        self.delegate = PyConWindowSignalExplorerDelegate(self)
        self.delegate.newSearch.connect(self.slot_search)

        self.__initUI()

        self.regex_indicator = "%"

        self.VIDEO_LINES_MAPPING = {
            "0": "left",
            "1": "right",
            "2": "leftLeft",
            "3": "rightRight",
            "4": "roadEdgeLeft",
            "5": "roadEdgeRight",
            "6": "roadEdgeLeftRaised",
            "7": "roadEdgeRightRaised",
        }

    def __initUI(self):
        initial_row_count = 3
        initial_col_count = 2
        # ======================================================================
        # table widget
        # ======================================================================
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(initial_row_count)
        self.table_widget.setColumnCount(initial_col_count)

        header = self.table_widget.horizontalHeader()

        self.table_widget.setHorizontalHeaderLabels(["Key", "Value"])

        # for idx in range(self.table_widget.rowCount()):
        #    self.table_widget.setRowHeight(idx, row_height)
        #    self.table_widget.setItemDelegateForRow(idx, self.delegate)

        self.table_widget.setItem(0, 0, QTableWidgetItem("File Name"))
        self.table_widget.setItem(0, 1, QTableWidgetItem("a full path here"))

        self.table_widget.setItem(1, 0, QTableWidgetItem("Search"))
        self.table_widget.setItemDelegateForRow(1, self.delegate)

        open_btn = QPushButton("Open")
        open_btn.setCheckable(True)
        open_btn.clicked.connect(self.open_yaml_file)

        self.table_widget.setCellWidget(2, 0, open_btn)
        self.table_widget.setItem(2, 1, QTableWidgetItem("Open yaml file"))

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        #
        # create tree view/model
        #
        self.signal_tree_view = QTreeView()
        self.signal_tree_view.setHeaderHidden(True)

        self.signal_tree_model = QStandardItemModel()
        self.signal_tree_model.setHorizontalHeaderLabels([self.tr("Signal Name")])
        self.root_node = self.signal_tree_model.invisibleRootItem()

        self.signal_tree_view.setModel(self.signal_tree_model)
        #
        # create a layout, containing :
        #  1. the table widget
        #  2. the tree view
        #
        _layout = QVBoxLayout()
        _layout.addWidget(self.table_widget, 3)
        _layout.addWidget(self.signal_tree_view, 7)
        #
        # widget of self
        #
        _widget = QWidget()
        _widget.setLayout(_layout)
        self.setWidget(_widget)

    def open_yaml_file(self):

        dlg = QFileDialog(directory=self.initial_yaml_dir)

        dlg.setNameFilters(get_pycon_config().pycon_start_yaml_filter)
        dlg.selectNameFilter(get_pycon_config().pycon_start_yaml_filter_selected)

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            selected_file_name = filenames[0]
            file_basename = os.path.basename(selected_file_name)
            self.open_dir = os.path.dirname(selected_file_name)
            file_basename_no_ext, file_basename_ext = os.path.splitext(file_basename)

            logger().info(selected_file_name)

            self.generic_yaml.open_yaml_file(yaml_file=selected_file_name)

            self.add_alias_signals()

    def add_alias_signals(self):

        self.signal_tree_view.model().removeRows(0, self.signal_tree_view.model().rowCount())

        std_item_found_signals = PyConStandardItem(
            channel_group_index=-1,
            channel_group_comment=None,
            channel_index=-1,
            text="found signals",
            font_size=12,
            set_bold=False,
        )
        self.root_node.appendRow(std_item_found_signals)

        for alias, signal in self.generic_yaml.alias_signal_dict.items():

            if self.search_text in alias:

                std_item_parent = PyConStandardItem(
                    channel_group_index=-1,
                    channel_group_comment=None,
                    channel_index=-1,
                    text=f"{alias}",
                    font_size=12,
                    set_bold=False,
                )
                channels = []
                std_item_signal = PyConStandardItem(
                    channel_group_index=-1,
                    channel_group_comment=None,
                    channel_index=-1,
                    text=f"{signal}",
                    font_size=12,
                    set_bold=False,
                )
                channels.append(std_item_signal)
                std_item_parent.appendRows(channels)
                std_item_found_signals.appendRow(std_item_parent)

        self.add_section(text="missing needed signals", sig_list=self.generic_yaml.missing_needed_signals)
        self.add_section(text="missing optional signals", sig_list=self.generic_yaml.missing_optional_signals)

        if self.search_text != "":
            self.signal_tree_view.expandAll()

    def add_section(self, text, sig_list):

        std_item_parent = PyConStandardItem(
            channel_group_index=-1,
            channel_group_comment=None,
            channel_index=-1,
            text=text,
            font_size=12,
            set_bold=False,
        )
        self.root_node.appendRow(std_item_parent)

        for signal in sig_list:

            if self.search_text in signal:

                std_item = PyConStandardItem(
                    channel_group_index=-1,
                    channel_group_comment=None,
                    channel_index=-1,
                    text=f"{signal}",
                    font_size=12,
                    set_bold=False,
                )

                std_item_parent.appendRow(std_item)

    # ==========================================================================
    # search
    # ==========================================================================
    def slot_timer_timeout(self):
        logger().info("timeout ... render result")
        self.timer.stop()
        self.timer_started = False

        self.add_alias_signals()

    def slot_search(self, search_text):
        logger().info(f"{search_text} ... {self.search_cnt}")

        self.search_text = search_text
        self.search_cnt = self.search_cnt + 1

        if not self.timer_started:
            self.timer.start(self.search_time_out)
            self.timer_started = True
        else:
            self.timer.stop()
            self.timer.start(self.search_time_out)
            self.timer_started = True
        return
