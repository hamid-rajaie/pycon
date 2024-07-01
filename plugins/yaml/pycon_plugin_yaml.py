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

        self.alias_signal_dict = params.alias_signal_dict
        self.missing_needed_signals = []
        self.missing_optional_signals = []

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

            with open(selected_file_name, "r") as file:
                yaml_data_dict = yaml.safe_load(file)

                self.parse_yaml(yaml_data_dict=yaml_data_dict)
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

        for alias, signal in self.alias_signal_dict.items():

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

        self.add_section(sig_list=self.missing_needed_signals)
        self.add_section(sig_list=self.missing_optional_signals)

        if self.search_text != "":
            self.signal_tree_view.expandAll()

    def add_section(self, sig_list):

        std_item_parent = PyConStandardItem(
            channel_group_index=-1,
            channel_group_comment=None,
            channel_index=-1,
            text="missing needed signals",
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

    def parse_yaml(self, yaml_data_dict: dict) -> tuple:

        self.missing_needed_signals = []
        self.missing_optional_signals = []

        self.alias_signal_dict = {}

        data_mf4 = self.pycon_data_source.data
        iter_mf4 = data_mf4.channels_db.keys()
        signals_mf4 = [channel.name for group in data_mf4.groups for channel in group.channels]

        for alias, alias_desc in yaml_data_dict.items():

            try:
                alias_signals = alias_desc["signal"]

                alias_optional = None
                if "optional" in alias_desc.keys():
                    alias_optional = alias_desc["signal"]

                signal_available = False

                if isinstance(alias_signals, list):

                    for _, alias_signal in enumerate(alias_signals):
                        if alias_signal in iter_mf4:
                            if self.regex_indicator not in alias_signal:
                                self.alias_signal_dict[alias] = alias_signal
                                signal_available = True
                                break
                        else:
                            if self.regex_indicator in alias_signal:
                                regex_indices_alias = [i for i, c in enumerate(alias) if c == self.regex_indicator]
                                regex_indices_signal = [
                                    i for i, c in enumerate(alias_signal) if c == self.regex_indicator
                                ]
                                regex_pattern = re.escape(
                                    alias_signal[: regex_indices_signal[0]]
                                )  # add the initial part of the string
                                for i, index in enumerate(regex_indices_signal):
                                    if i == 0:
                                        continue  # skip the first occurrence since it was already added
                                    prev_index = regex_indices_signal[i - 1]
                                    regex_pattern += r"(?P<index{}_>\d+)".format(i)  # add the named capturing group
                                    regex_pattern += re.escape(
                                        alias_signal[prev_index + 1 : index]
                                    )  # add the text between the % and the next occurrence
                                regex_pattern += r"(?P<index{}_>\d+)".format(
                                    len(regex_indices_signal)
                                )  # add the final named capturing group
                                regex_pattern += re.escape(
                                    alias_signal[regex_indices_signal[-1] + 1 :]
                                )  # add the final part of the string

                                # find all matches
                                matches = re.findall(regex_pattern, str(signals_mf4))
                                if matches:
                                    for match in matches:
                                        if not isinstance(match, tuple):
                                            match = [match]
                                        new_alias = alias
                                        new_signal = alias_signal
                                        for pos, index in enumerate(match):
                                            new_alias = (
                                                new_alias[: regex_indices_alias[pos]]
                                                + index
                                                + new_alias[regex_indices_alias[pos] + 1 :]
                                            )
                                            new_signal = (
                                                new_signal[: regex_indices_signal[pos]]
                                                + index
                                                + new_signal[regex_indices_signal[pos] + 1 :]
                                            )
                                        # for videoLines we need to map the alias name back!
                                        if "videoLines" in new_alias and "polynomialLine" not in new_alias:
                                            # index:    11 12
                                            # videoLines.X.
                                            new_alias = (
                                                new_alias[:11]
                                                + self.VIDEO_LINES_MAPPING.get(match[0], f"UNKOWN-{new_alias[11]}")
                                                + new_alias[12:]
                                            )
                                        self.alias_signal_dict[new_alias] = new_signal
                                        signal_available = True

                                if signal_available:
                                    break
                if not signal_available and alias_optional is not None:
                    self.missing_optional_signals.append(alias)
                if not signal_available and alias_optional is None:
                    self.missing_needed_signals.append(alias)
            except Exception as exp:
                logger().warning(f"alias: {alias}  {str(exp)}")

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
