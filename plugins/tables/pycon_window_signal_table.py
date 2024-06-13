import numpy as np
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView, QVBoxLayout, QWidget

from common.delegates.pycon_window_read_only_delegate import PyConWindowReadOnlyDelegate
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams


class PyConWindowSignalTableModel(QtCore.QAbstractTableModel):
    def __init__(self, selected_signals: dict, selected_signals_columns: dict):
        super().__init__()
        # self.df = df
        self.selected_signals = selected_signals
        self.selected_signals_columns = selected_signals_columns
        self.highlighted_row = None
        self.header = []

    def data(self, model_index, role):
        elem = ""
        if role == QtCore.Qt.DisplayRole:
            row_index = model_index.row()
            col_index = model_index.column()
            # col_name = self.df.columns[col_index]
            signal = self.selected_signals_columns[col_index]
            # elem = self.df.at[row_index, col_name]
            elem = f"{signal[row_index]}"
            return str(elem)

        elif role == QtCore.Qt.BackgroundRole:
            if model_index.row() == self.highlighted_row:
                return QtGui.QColor("yellow")

    def set_highlighted_row(self, index):
        self.highlighted_row = index
        self.layoutChanged.emit()

    def itemFromIndex(self, index: QtCore.QModelIndex):
        return super().itemFromIndex(index)

    def rowCount(self, model_index):
        count = 0
        for group_index, group in self.selected_signals.items():
            for channel_index, channel in group.items():
                channel_name = channel["channel_name"]
                time = channel["time"]
                signal = channel["signal"]
                count = max(count, signal.size)
        return count

    def columnCount(self, model_index):
        return len(self.header)

    def headerData(self, section, orientation, role):
        self.header = []
        for group_index, group in self.selected_signals.items():
            for channel_index, channel in group.items():
                channel_name = channel["channel_name"]
                time = channel["time"]
                signal = channel["signal"]
                self.header.append(channel_name)

        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.header[section]
            else:
                return str(section + 1)


class PyConWindowSignalTable(PyConPluginBase):
    # ==================================================
    # SIGNALS
    # ==================================================
    removeSignal = QtCore.pyqtSignal(str)
    removeAllSignals = QtCore.pyqtSignal()

    def __init__(self, params: PyConPluginParams):
        super().__init__()

        uic.loadUiType("plugins/tables/pycon_window_signal_table.ui", self)

        self.df = params.pycon_data_source

        self.signals_shown = []
        self.df_shown = None

        self.win_widget = None
        self.table_view = None
        self.table_view_header = None
        self.model = None

        self.setWindowTitle("Signal View")
        self.resize(900, 400)
        self.delegate = PyConWindowReadOnlyDelegate(self)

        self.selected_signals = {}
        self.selected_signals_columns = {}

        self.__initUI()
        # When you create your own sub window, you must set the WA_DeleteOnClose widget attribute
        # if you want the window to be deleted when closed in the MDI area.
        # If not, the window will be hidden and the MDI area will not activate the next sub window.
        # self.setAttribute(Qt.WA_DeleteOnClose, wa_delete_on_close)

    def __initUI(self):
        # https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QTableView.html
        # https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QAbstractItemView.html
        # https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QHeaderView.html

        # https://doc.qt.io/qtforpython-5/PySide2/QtCore/QAbstractTableModel.html
        # https://doc.qt.io/qtforpython-5/PySide2/QtCore/QAbstractItemModel.html
        #
        # table view
        #
        self.table_view = QTableView(self)
        self.table_view.horizontalHeader().setStretchLastSection(True)

        self.table_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.open_table_context_menu)
        #
        # header of table view
        #
        self.table_view_header = self.table_view.horizontalHeader()
        self.table_view_header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table_view_header.customContextMenuRequested.connect(self.open_header_context_menu)

        self.table_view.doubleClicked.connect(self.__print_selected_cell)

        #
        # create a layout, containing :
        #  1. the table view
        #
        _layout = QVBoxLayout()
        _layout.addWidget(self.table_view)
        #
        # widget of self
        #
        self.win_widget = QWidget()
        self.win_widget.setLayout(_layout)
        self.setWidget(self.win_widget)

    def open_header_context_menu(self, pos):
        """
        open a context menu for the header ( not the rows )

        :param pos: PyQt5.QtCore.QPoint object
        """
        pass

    def open_table_context_menu(self, pos: QtCore.QPoint):
        """
        open a context menu for the table ( rows but not the header )

        :param pos: PyQt5.QtCore.QPoint object
        :return:
        """
        pass

    @QtCore.pyqtSlot(int)
    def highlight_and_scroll_to_row(self, row_index):
        if self.model:
            self.model.set_highlighted_row(row_index)
            self.table_view.scrollTo(self.model.index(row_index, 0), QTableView.PositionAtCenter)

    @QtCore.pyqtSlot(int, int, str, np.ndarray, np.ndarray)
    def slot_add_signal_by_double_click(self, group_index, channel_index, channel_name, time, signal):
        if group_index not in self.selected_signals.keys():
            self.selected_signals[group_index] = {}

        if channel_index not in self.selected_signals[group_index]:
            self.selected_signals[group_index][channel_index] = {}

        self.selected_signals[group_index][channel_index] = {
            "channel_name": channel_name,
            "time": time,
            "signal": signal,
            # "std_item_val": std_item_val,
        }
        self.selected_signals_columns[len(self.selected_signals_columns.keys())] = signal

        #
        # create a model
        #
        self.model = PyConWindowSignalTableModel(self.selected_signals, self.selected_signals_columns)
        self.table_view.setModel(self.model)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def __print_selected_cell(self, modelIndex: QtCore.QModelIndex):
        col = modelIndex.column()
        row = modelIndex.row()
        data = modelIndex.data()

        mdl = modelIndex.model()

        header_model = self.table_view.horizontalHeader().model()

        if False:
            for column in range(header_model.columnCount(None)):
                header_data = header_model.headerData(column, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
                print(f"PyConWindowSignalTable.__print_selected_cell  header_data:{header_data}")

        header_data = header_model.headerData(col, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)

        print(f"click on cel[{row}][{col}] : {data} --> signal_name:{header_data}")
