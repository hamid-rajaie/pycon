import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QHeaderView, QMenu, QTableWidget, QTableWidgetItem, QTreeView, QVBoxLayout, QWidget

from common.delegates.pycon_window_signal_explorer_delegate import PyConWindowSignalExplorerDelegate
from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from container.pycon_dialog_wait import PyConDialogWait
from data_sources.pycon_data_source import PyConDataSource
from data_sources.pycon_standard_item import PyConStandardItem
from pycon_config import get_pycon_config


class PyConPluginSignalExplorer(PyConPluginBase):
    # ==================================================
    # SIGNALS
    # ==================================================
    signal_explorer_double_click = QtCore.pyqtSignal(int, int, str, np.ndarray, np.ndarray)

    def __init__(self, pycon_data_source: PyConDataSource):
        super().__init__()

        self.pycon_data_source = pycon_data_source

        self.setWindowTitle("Signal Explorer")
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

    def __initUI(self):
        initial_row_count = 2
        initial_col_count = 2
        # ======================================================================
        # table widget
        # ======================================================================
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(initial_row_count)
        self.table_widget.setColumnCount(initial_col_count)

        header = self.table_widget.horizontalHeader()

        self.table_widget.setHorizontalHeaderLabels(["Key", "Value"])

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

    def init_data(self):
        self.add_signals_to_tree_view()

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
    # double click
    # ==========================================================================
    def slot_signal_tree_view_double_clicked(self, modelIndex):
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
    def add_signals_to_tree_view(self):

        self.signal_tree_view.model().removeRows(0, self.signal_tree_view.model().rowCount())

        for group_index, group in enumerate(self.pycon_data_source.data.groups):
            channel_group = group.channel_group
            channel_group_comment = channel_group.comment

            std_item_channel_group = None

            channels = []
            for channel_index, channel in enumerate(group.channels):
                if self.search_text in channel.name:
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

                self.root_node.appendRow(std_item_channel_group)

        # self.signal_tree_view.setModel(self.signal_tree_model)
        if self.search_text != "":
            pass
            self.signal_tree_view.expandAll()
