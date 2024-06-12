from PyQt5 import QtCore
from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate, QTextEdit, QWidget


class PyConWindowReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return
