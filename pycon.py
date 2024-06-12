import sys

sys.path.append("../../")

from PyQt5.QtWidgets import QApplication

from main_window.pycon_main_window import PyConMainWindow

# main
if __name__ == "__main__":
    app = QApplication(sys.argv)

    pyConMainWindow = PyConMainWindow()

    sys.exit(app.exec_())
