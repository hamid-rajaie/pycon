from PyQt5.QtWidgets import QApplication, QDialog, QDialogButtonBox, QLabel, QVBoxLayout


class PyConDialogWait(QDialog):

    def __init__(self, parent, message):
        super().__init__(parent)

        self.setWindowTitle("Wait")
        self.resize(500, 100)

        # QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        # self.buttonBox = QDialogButtonBox(QBtn)
        # self.buttonBox.accepted.connect(self.accept)
        # self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(message)
        self.layout.addWidget(message)
        # self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.open()
        QApplication.processEvents()

    def hide_dialog(self):
        self.hide()
        QApplication.processEvents()
