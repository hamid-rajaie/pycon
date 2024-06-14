from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QPlainTextEdit, QVBoxLayout, QWidget


class PyConAboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # uic.loadUi("container/pycon_main_window_dialog_about.ui", self)

        self.setWindowTitle("About PyCon Analyzer")

        self.white_board = None

        self._create_objects()

    def _create_objects(self):
        self.white_board = QPlainTextEdit()
        self.white_board.appendPlainText("written by Hamid Rajaie")
        _layout = QVBoxLayout()
        _layout.addWidget(self.white_board)
        self.setLayout(_layout)
