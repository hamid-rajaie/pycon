import os

import numpy as np
import yaml
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (
    QFileDialog,
    QHeaderView,
    QMenu,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from common.delegates.pycon_window_signal_explorer_delegate import PyConWindowSignalExplorerDelegate
from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from container.pycon_dialog_wait import PyConDialogWait
from data_sources.pycon_data_source_base import PyConDataSourceBase
from data_sources.pycon_standard_item import PyConStandardItem
from pycon_config import get_pycon_config


class PyConPluginSignalExplorer(PyConPluginBase):
    # ==================================================
    # SIGNALS
    # ==================================================
    signal_explorer_double_click = QtCore.pyqtSignal(int, int, str, np.ndarray, np.ndarray)

    def __init__(self, params: PyConPluginParams):
        super().__init__()

        self.pycon_data_source = params.pycon_data_source
        self.initial_yaml_dir = params.initial_yaml_dir

        self.setWindowTitle("Signal Explorer")
        #
        # read csv
        #
        self.data_frame = None

        self.signal_tree_model_0 = None
        self.signal_tree_view_0 = None
        self.root_node_0 = None
        self.root_node_1 = None

        self.timer_0 = QTimer(self)
        self.timer_0.timeout.connect(self.slot_timer_timeout_0)
        self.timer_started_0 = False

        self.timer_1 = QTimer(self)
        self.timer_1.timeout.connect(self.slot_timer_timeout_1)
        self.timer_started_1 = False

        self.search_time_out = 1000

        self.search_text_0 = ""
        self.search_cnt_0 = 0

        self.search_text_1 = ""
        self.search_cnt_1 = 0

        self.delegate_0 = PyConWindowSignalExplorerDelegate(self)
        self.delegate_0.newSearch.connect(self.slot_search_0)

        self.delegate_1 = PyConWindowSignalExplorerDelegate(self)
        self.delegate_1.newSearch.connect(self.slot_search_1)

        self.tab_widget = None

        self.__initUI()

    def __initUI(self):

        self.tab_widget = QTabWidget()

        _widget_0 = self.tab_0()
        _widget_1 = self.tab_1()

        self.tab_widget.addTab(_widget_0, "Explorer")
        self.tab_widget.addTab(_widget_1, "Alias")
        self.setWidget(self.tab_widget)

    def initPlugin(self):
        self.add_signals_to_tree_view_0()

    def tab_0(self):
        initial_row_count = 2
        initial_col_count = 2
        # ======================================================================
        # table widget
        # ======================================================================
        table_widget_0 = QTableWidget()
        table_widget_0.setRowCount(initial_row_count)
        table_widget_0.setColumnCount(initial_col_count)

        header_0 = table_widget_0.horizontalHeader()

        table_widget_0.setHorizontalHeaderLabels(["Key", "Value"])

        table_widget_0.setItem(0, 0, QTableWidgetItem("File Name"))
        table_widget_0.setItem(0, 1, QTableWidgetItem("a full path here"))

        table_widget_0.setItem(1, 0, QTableWidgetItem("Search"))
        table_widget_0.setItemDelegateForRow(1, self.delegate_0)

        header_0.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header_0.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        #
        # create tree view/model
        #
        self.signal_tree_view_0 = QTreeView()
        self.signal_tree_view_0.setHeaderHidden(True)
        self.signal_tree_view_0.doubleClicked.connect(self.slot_signal_tree_view_0_double_clicked)

        self.signal_tree_model_0 = QStandardItemModel()
        self.signal_tree_model_0.setHorizontalHeaderLabels([self.tr("Signal Name")])
        self.root_node_0 = self.signal_tree_model_0.invisibleRootItem()

        self.signal_tree_view_0.setModel(self.signal_tree_model_0)
        #
        # create a layout, containing :
        #  1. the table widget
        #  2. the tree view
        #
        _layout_0 = QVBoxLayout()
        _layout_0.addWidget(table_widget_0, 3)
        _layout_0.addWidget(self.signal_tree_view_0, 7)
        #
        # widget of self
        #
        _widget_0 = QWidget()
        _widget_0.setLayout(_layout_0)

        return _widget_0

    def tab_1(self):
        initial_row_count = 3
        initial_col_count = 2
        # ======================================================================
        # table widget
        # ======================================================================
        table_widget_1 = QTableWidget()
        table_widget_1.setRowCount(initial_row_count)
        table_widget_1.setColumnCount(initial_col_count)

        header_1 = table_widget_1.horizontalHeader()

        table_widget_1.setHorizontalHeaderLabels(["Key", "Value"])

        table_widget_1.setItem(0, 0, QTableWidgetItem("File Name"))
        table_widget_1.setItem(0, 1, QTableWidgetItem("a full path here"))

        table_widget_1.setItem(1, 0, QTableWidgetItem("Search"))
        table_widget_1.setItemDelegateForRow(1, self.delegate_1)

        open_btn = QPushButton("Open")
        open_btn.setCheckable(True)
        open_btn.clicked.connect(self.open_yaml_file)

        table_widget_1.setCellWidget(2, 0, open_btn)
        table_widget_1.setItem(2, 1, QTableWidgetItem("Open yaml file"))

        header_1.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header_1.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        # ======================================================================
        # create tree view/model
        # ======================================================================
        self.signal_tree_view_1 = QTreeView()
        self.signal_tree_view_1.setHeaderHidden(False)
        self.signal_tree_view_1.header().setStretchLastSection(False)
        self.signal_tree_view_1.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        signal_tree_model_1 = QStandardItemModel()
        signal_tree_model_1.setHorizontalHeaderLabels([self.tr("Signal Name")])
        self.root_node_1 = signal_tree_model_1.invisibleRootItem()

        self.signal_tree_view_1.setModel(signal_tree_model_1)
        # ======================================================================
        # create a layout, containing :
        #  1. the table widget
        #  2. the tree view
        # ======================================================================
        _layout_1 = QVBoxLayout()
        _layout_1.addWidget(table_widget_1, 3)
        _layout_1.addWidget(self.signal_tree_view_1, 7)
        # ======================================================================
        # add widget
        # ======================================================================
        _widget_1 = QWidget()
        _widget_1.setLayout(_layout_1)
        return _widget_1

    # ==========================================================================
    # search
    # ==========================================================================
    def slot_timer_timeout_0(self):
        logger().info("timeout 0 ... render result")
        self.timer_0.stop()
        self.timer_started_0 = False

        self.add_signals_to_tree_view_0()

    def slot_timer_timeout_1(self):
        logger().info("timeout 1 ... render result")
        self.timer_1.stop()
        self.timer_started_1 = False

        self.add_signals_to_tree_view_1()

    def slot_search_0(self, search_text_0):

        self.search_text_0 = search_text_0
        self.search_cnt_0 = self.search_cnt_0 + 1

        if not self.timer_started_0:
            self.timer_0.start(self.search_time_out)
            self.timer_started_0 = True
        else:
            self.timer_0.stop()
            self.timer_0.start(self.search_time_out)
            self.timer_started_0 = True
        return

    def slot_search_1(self, search_text_1):

        self.search_text_1 = search_text_1
        self.search_cnt_1 = self.search_cnt_1 + 1

        if not self.timer_started_1:
            self.timer_1.start(self.search_time_out)
            self.timer_started_1 = True
        else:
            self.timer_1.stop()
            self.timer_1.start(self.search_time_out)
            self.timer_started_1 = True
        return

    # ==========================================================================
    # double click
    # ==========================================================================
    def slot_signal_tree_view_0_double_clicked(self, modelIndex):
        """
        :param modelIndex: a PyQt5.QtCore.QModelIndex
        """
        if not modelIndex.parent().isValid():
            # root node is selected
            logger().warning("you have double clicked on a channel")
            return

        channel_name = modelIndex.data()
        standardItem = modelIndex.model().itemFromIndex(modelIndex)
        channel_group_index = standardItem.channel_group_index
        channel_index = standardItem.channel_index

        parentStandardItem = modelIndex.parent().model().itemFromIndex(modelIndex.parent())
        channel_group_comment = parentStandardItem.text()

        channel_index_timestamp = 0

        time = None

        for sig_time in get_pycon_config().pycon_time_signals:
            try:
                time = self.pycon_data_source.get_channel(channel_name=sig_time, group_index=channel_group_index)
                # logger().info(f"{sig_time} found")
            except Exception:
                # logger().warning(f"{sig_time} not found")
                pass

        if time is None:
            logger().warning("no time signal found")
            return

        try:
            signal = self.pycon_data_source.get_channel(
                channel_name=channel_name, group_index=channel_group_index, channel_index=channel_index
            )
            #
            # type(signal.samples) is <class 'numpy.ndarray'>
            #
            self.signal_explorer_double_click.emit(
                channel_group_index,
                channel_index,
                channel_name,
                time.samples,
                signal.samples,
            )

        except Exception as ex:
            logger().warning(str(ex))

    # ==========================================================================
    # add signals
    # ==========================================================================
    def add_signals_to_tree_view_0(self):

        self.signal_tree_view_0.model().removeRows(0, self.signal_tree_view_0.model().rowCount())

        for group_index, group in enumerate(self.pycon_data_source.data.groups):
            channel_group = group.channel_group
            channel_group_comment = channel_group.comment

            std_item_channel_group = None

            channels = []
            for channel_index, channel in enumerate(group.channels):
                if self.search_text_0 in channel.name:
                    if std_item_channel_group is None:
                        std_item_channel_group = PyConStandardItem(
                            channel_group_index=-1,
                            channel_group_comment=channel_group_comment,
                            channel_index=-1,
                            text=f"Channel Group {group_index} " f"({channel_group_comment}) ",
                            font_size=12,
                            set_bold=False,
                        )

                    std_item_ch = PyConStandardItem(
                        channel_group_index=group_index,
                        channel_group_comment=channel_group_comment,
                        channel_index=channel_index,
                        text=f"{channel.name}",
                        font_size=12,
                        set_bold=False,
                    )
                    channels.append(std_item_ch)

            if std_item_channel_group is not None:
                std_item_channel_group.appendRows(channels)

                self.root_node_0.appendRow(std_item_channel_group)

        # self.signal_tree_view_0.setModel(self.signal_tree_model_0)
        if self.search_text_0 != "":
            pass
            self.signal_tree_view_0.expandAll()

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

            with open(selected_file_name, "r") as file:
                yaml_data_dict = yaml.safe_load(file)
                dlg_wait = PyConDialogWait(self, "Parsing yaml")
                self.pycon_data_source.setup_generic_real_map(yaml_data_dict=yaml_data_dict)
                self.pycon_data_source.get_channels()
                dlg_wait.hide_dialog()
                self.add_signals_to_tree_view_1()

    def add_signals_to_tree_view_1(self):

        self.signal_tree_view_1.model().removeRows(0, self.signal_tree_view_1.model().rowCount())

        std_item_found_signals = PyConStandardItem(
            channel_group_index=-1,
            channel_group_comment=None,
            channel_index=-1,
            text="found signals",
            font_size=12,
            set_bold=False,
        )
        self.root_node_1.setColumnCount(2)
        self.root_node_1.appendRow(std_item_found_signals)

        for alias, pycon_signal in self.pycon_data_source.generic_to_real_map.items():

            signal = pycon_signal.real_signal_name

            if self.search_text_1 in alias or self.search_text_1 in signal:

                std_item_alias = PyConStandardItem(
                    channel_group_index=-1,
                    channel_group_comment=None,
                    channel_index=-1,
                    text=f"{alias}",
                    font_size=12,
                    set_bold=False,
                )

                std_item_signal = PyConStandardItem(
                    channel_group_index=-1,
                    channel_group_comment=None,
                    channel_index=-1,
                    text=f"{signal}",
                    font_size=12,
                    set_bold=False,
                )

                std_item_found_signals.appendRow((std_item_alias, std_item_signal))

        self.add_section_1(
            text="missing needed generic signals", sig_list=self.pycon_data_source.missing_needed_generic_signals()
        )
        self.add_section_1(
            text="missing optional generic signals",
            sig_list=self.pycon_data_source.missing_optional_generic_signals(),
        )

        if self.search_text_1 != "":
            self.signal_tree_view_0.expandAll()

    def add_section_1(self, text, sig_list):

        std_item_alias = PyConStandardItem(
            channel_group_index=-1,
            channel_group_comment=None,
            channel_index=-1,
            text=text,
            font_size=12,
            set_bold=False,
        )
        self.root_node_1.appendRow(std_item_alias)

        for signal in sig_list:

            if self.search_text_1 in signal:

                std_item = PyConStandardItem(
                    channel_group_index=-1,
                    channel_group_comment=None,
                    channel_index=-1,
                    text=f"{signal}",
                    font_size=12,
                    set_bold=False,
                )

                std_item_alias.appendRow(std_item)
