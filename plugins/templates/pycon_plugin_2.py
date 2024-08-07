import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QHeaderView, QMenu, QTableWidget, QTableWidgetItem, QTreeView, QVBoxLayout, QWidget

from common.delegates.pycon_window_signal_explorer_delegate import PyConWindowSignalExplorerDelegate
from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from data_sources.pycon_data_source_base import PyConDataSourceBase
from data_sources.pycon_standard_item import PyConStandardItem


class PyConWindowPlugin_2(PyConPluginBase):
    # ==================================================
    # SIGNALS
    # ==================================================
    signal_explorer_double_click = QtCore.pyqtSignal(int, int, str, np.ndarray, np.ndarray)

    def __init__(self, params: PyConPluginParams):
        super().__init__()

        self.pycon_data_source = params.pycon_data_source

        self.setWindowTitle("Plugin 2")
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

        self.add_signals_to_tree_view()

    def __initUI(self):
        initial_row_count = 2
        initial_col_count = 2
        #
        # table widget
        #
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(initial_row_count)
        self.table_widget.setColumnCount(initial_col_count)

        self.table_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.open_table_widget_rows_context_menu)

        header = self.table_widget.horizontalHeader()
        header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self.open_table_widget_header_context_menu)

        self.table_widget.setHorizontalHeaderLabels(["Key", "Value"])

        # for idx in range(self.table_widget.rowCount()):
        #    self.table_widget.setRowHeight(idx, row_height)
        #    self.table_widget.setItemDelegateForRow(idx, self.delegate)

        self.table_widget.setItem(0, 0, QTableWidgetItem("File Name"))
        self.table_widget.setItem(0, 1, QTableWidgetItem("a full path here"))

        self.table_widget.setItem(1, 0, QTableWidgetItem("Search"))
        self.table_widget.setItemDelegateForRow(1, self.delegate)

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        #
        # create tree view/model
        #
        self.signal_tree_view = QTreeView()
        self.signal_tree_view.setHeaderHidden(True)
        self.signal_tree_view.doubleClicked.connect(self.slot_signal_tree_view_double_clicked)

        self.signal_tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.signal_tree_view.customContextMenuRequested.connect(self.open_signal_tree_view_context_menu)

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

    # ==========================================================================
    # search
    # ==========================================================================
    def slot_timer_timeout(self):
        logger().info("timeout ... render result")
        self.timer.stop()
        self.timer_started = False

        self.add_signals_to_tree_view()

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

    # ==========================================================================
    # context menu
    # ==========================================================================
    def open_table_widget_header_context_menu(self, pos):
        """
        open a context menu for the header ( not the rows )

        :param pos: PyQt5.QtCore.QPoint object
        """
        logger().info("")

    # ==========================================================================
    # context menu
    # ==========================================================================
    def open_table_widget_rows_context_menu(self, pos):
        """
        open a context menu for the table ( rows but not the header )

        :param pos: PyQt5.QtCore.QPoint object
        """

        model_index = self.table_widget.indexAt(pos)
        if not model_index.isValid():
            logger().info("model_index is not valid")
            return
        else:
            logger().info("modelIndex is valid")
        #
        # open context menu
        #
        menu = QMenu(self)
        view_all_signals_action = menu.addAction("Table View")
        action = menu.exec_(self.table_widget.mapToGlobal(pos))
        if action == view_all_signals_action:
            logger().info("")

    # ==========================================================================
    # context menu
    # ==========================================================================
    def open_signal_tree_view_context_menu(self, pos):
        """
        open a context menu for the tree view

        :param pos: PyQt5.QtCore.QPoint object
        """
        #
        # todo, you can delete the following
        #
        # indexes = self.signal_tree_view.selectedIndexes()
        index = self.signal_tree_view.selectedIndexes()[0]
        item = index.model().itemFromIndex(index)
        channel_name = item.text()
        #
        # open context menu
        #
        menu = QMenu(self)
        action_1 = menu.addAction("Action 1")
        action = menu.exec_(self.signal_tree_view.viewport().mapToGlobal(pos))
        if action == action_1:
            logger().info(f"channel_name : {channel_name}")

    # ==========================================================================
    # double click
    # ==========================================================================
    def slot_signal_tree_view_double_clicked(self, modelIndex):
        """
        :param modelIndex: a PyQt5.QtCore.QModelIndex
        """
        if not modelIndex.parent().isValid():
            # root node is selected
            logger().warning("you have double clicked on a parent")
            return

        channel_name = modelIndex.data()
        standardItem = modelIndex.model().itemFromIndex(modelIndex)
        channel_group_index = standardItem.channel_group_index
        channel_index = standardItem.channel_index

        parentStandardItem = modelIndex.parent().model().itemFromIndex(modelIndex.parent())
        channel_group_comment = parentStandardItem.text()

        logger().info(f"channel name : {channel_name}")

    # ==========================================================================
    # add signals
    # ==========================================================================
    def add_signals_to_tree_view(self):
        self.signal_tree_view.model().removeRows(0, self.signal_tree_view.model().rowCount())

        for parent in ["parent_1", "parent_2"]:
            std_item_parent = PyConStandardItem(
                channel_group_index=-1,
                channel_group_comment=None,
                channel_index=-1,
                text=parent,
                font_size=12,
                set_bold=False,
            )
            self.root_node.appendRow(std_item_parent)
            signals = []
            for signal in ["sig 1", "sig 2"]:
                std_item = PyConStandardItem(
                    channel_group_index=-1,
                    channel_group_comment=None,
                    channel_index=-1,
                    text=signal,
                    font_size=12,
                    set_bold=False,
                )
                signals.append(std_item)
                std_item_parent.appendRows(signals)

        if self.search_text != "":
            self.signal_tree_view.expandAll()
