from PyQt5 import QtCore
from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate, QTextEdit, QWidget

from common.logging.logger import logger


class PyConWindowSignalExplorerDelegate(QStyledItemDelegate):
    """
    https://doc.qt.io/archives/qt-4.8/model-view-programming.html#a-simple-delegate
    """

    # ==================================================
    # SIGNALS
    # ==================================================
    newSearch = QtCore.pyqtSignal(str)

    def __init__(self, parent: QtCore.QObject | None = ...) -> None:
        super().__init__(parent)
        self.new_search_count = 0

    def createEditor(self, parent, option, index):
        if index.row() in [0]:
            return
        if index.row() == 1 and index.column() == 0:
            return
        if index.row() == 1 and index.column() == 1:
            editor = QTextEdit(parent)
            editor.textChanged.connect(self.slot_editor_text_changed)
            return editor

    def slot_editor_text_changed(self):
        editor = self.sender()
        if isinstance(editor, QTextEdit):
            logger().info(f"search text editor send signal .... {self.new_search_count}")
            self.newSearch.emit(editor.toPlainText())
            self.new_search_count = self.new_search_count + 1

    def setEditorData(self, editor, index):
        """
        will be called:
            - when we start to edit
            - when we are done
        :param editor: type: QWidget, is the editor we have created
        :param index: type: QModelIndex
        """

        if index.column() == 0:
            pass
        if index.column() == 1:
            editor.setText(index.data())

    def setModelData(self, editor, model, index):
        """
        will be called when we are done with editing.
        """

        if index.column() == 0:
            pass
        if index.column() == 1:
            if isinstance(editor, QTextEdit):
                model.setData(index, editor.toPlainText())

                if isinstance(editor, QTextEdit):
                    model.setData(index, editor.toPlainText())
                else:
                    super().setModelData(editor, model, index)
