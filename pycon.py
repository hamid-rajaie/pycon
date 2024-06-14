import sys

sys.path.append("../../")

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication

from container.pycon_main_window import PyConMainWindow

# main
if __name__ == "__main__":
    app = QApplication(sys.argv)

    pyConMainWindow = PyConMainWindow()

    sys.exit(app.exec_())
