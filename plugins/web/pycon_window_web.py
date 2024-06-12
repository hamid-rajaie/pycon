from PyQt5 import QtCore, uic
from PyQt5.QtCore import QEvent, QObject, QUrl, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams


class Backend(QObject):
    @pyqtSlot(str)
    def process_data(self, data):
        print(f"Data received: {data}")


class PyConWindowWeb(PyConPluginBase):

    def __init__(self, params: PyConPluginParams):
        super().__init__()

        uic.loadUiType("plugins/web/pycon_window_web.ui", self)
        self.setWindowTitle("Web")

        self.win_widget = None
        self.web_view = None
        self.backend = Backend()
        self.channel = QWebChannel()
        self.channel.registerObject("backend", self.backend)

        self.initUI()

    def initUI(self):
        self.web_view = QWebEngineView()
        self.web_view.page().setWebChannel(self.channel)

        _layout = QVBoxLayout()
        _layout.addWidget(self.web_view)

        self.win_widget = QWidget()
        self.win_widget.setLayout(_layout)
        self.setWidget(self.web_view)

    def eventFilter(self, obj, event):
        # If the AppWindow widget is shown on screen.
        if obj == self.widget() and event.type() == event.Close and obj.close():
            self.close()
            return True
        if event.type() == QEvent.Show:
            logger().info("The AppWindow shown event was captured")
            # Return true to inform that this event was consumed.
            self.load()
            return True
        # Return the object and event.
        return super().eventFilter(obj, event)

    def load(self):
        url = QUrl("http://www.google.de/")
        self.web_view.load(url)
