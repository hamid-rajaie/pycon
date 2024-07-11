import numpy as np
from PyQt5 import QtCore
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QAction, QMenu, QMenuBar, QTreeView, QVBoxLayout, QWidget

from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from common.pycon_numpy import find_nearest_time
from data_sources.pycon_standard_item import PyConStandardItem
from plugins_std.pycon_time import PyConTime


class PyConWindowSelectedSignals(PyConPluginBase):

    def __init__(self, params: PyConPluginParams):
        super().__init__()

        self.setWindowTitle("Selected Signals")
        #
        # read csv
        #
        self.data_frame = None

        self.table_widget = None
        self.signal_tree_model = None
        self.signal_tree_view = None
        self.root_node = None

        self.selected_signals = {}

        self.__initUI()

    def __initUI(self):
        #
        # create tree view/model
        #
        self.signal_tree_view = QTreeView()
        self.signal_tree_view.setHeaderHidden(False)

        self.signal_tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.signal_tree_view.customContextMenuRequested.connect(self.open_signal_tree_view_context_menu)

        self.signal_tree_model = QStandardItemModel()
        self.signal_tree_model.setHorizontalHeaderLabels(["Signal Name", "Signal Value"])
        self.root_node = self.signal_tree_model.invisibleRootItem()

        self.signal_tree_view.setModel(self.signal_tree_model)

        super().initUI(widget=self.signal_tree_view, with_menubar=False)

    # ==========================================================================
    # context menu
    # ==========================================================================
    def open_signal_tree_view_context_menu(self, pos):
        """
        open a context menu for the tree view

        :param pos: PyQt5.QtCore.QPoint object
        """

        logger().info("")
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
        action_remove_signal = menu.addAction("Remove Signal")
        action = menu.exec_(self.signal_tree_view.viewport().mapToGlobal(pos))
        if action == action_remove_signal:
            logger().info(f"channel_name : {channel_name}")

    @QtCore.pyqtSlot(int, int, str, np.ndarray, np.ndarray)
    def slot_add_signal_by_double_click(self, group_index, channel_index, channel_name, time, signal):
        self.show()

        std_item_ch = PyConStandardItem(
            channel_group_index=group_index,
            channel_group_comment="",
            channel_index=channel_index,
            text=channel_name,
            font_size=12,
            set_bold=False,
        )

        std_item_val = PyConStandardItem(
            channel_group_index=group_index,
            channel_group_comment="",
            channel_index=channel_index,
            text="...",
            font_size=12,
            set_bold=False,
        )
        self.root_node.appendRow([std_item_ch, std_item_val])

        if group_index not in self.selected_signals.keys():
            self.selected_signals[group_index] = {}

        if channel_index not in self.selected_signals[group_index]:
            self.selected_signals[group_index][channel_index] = {}

        self.selected_signals[group_index][channel_index] = {
            "channel_name": channel_name,
            "time": time,
            "signal": signal,
            "std_item_val": std_item_val,
        }

    @QtCore.pyqtSlot(PyConTime)
    def slider_value_changed(self, time: PyConTime):

        time_sec = time.get_time_sec()

        for group_index, group in self.selected_signals.items():
            for channel_index, channel in group.items():
                channel_name = channel["channel_name"]
                time = channel["time"]
                idx, t = find_nearest_time(arr=time, value=time_sec)

                signal = channel["signal"]
                std_item_val = channel["std_item_val"]

                signal_value = signal[idx]
                std_item_val.setText(str(signal_value))
