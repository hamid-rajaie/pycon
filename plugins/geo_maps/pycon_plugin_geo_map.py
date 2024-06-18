import io

import folium
from jinja2 import Template
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from common.pycon_numpy import find_nearest_time
from plugins.geo_maps.controls.pycon_folium_click import PyConFoliumClick
from plugins_std.pycon_time import PyConTime


class Backend(QObject):
    @pyqtSlot(str)
    def process_data(self, data):
        print(f"Data received: {data}")


class PyConPluginGeoMap(PyConPluginBase):
    """
    lon_wgs84: INS_Long_Abs
    lat_wgs84: INS_Lat_Abs
    """

    # ==================================================
    # SIGNALS
    # ==================================================
    signal_time_loaded = QtCore.pyqtSignal(float, float)

    def __init__(self, params: PyConPluginParams):
        super().__init__()

        self.pycon_data_source = params.pycon_data_source

        self.setWindowTitle("Geo Map")

        self.win_widget = None
        self.geo_map_view = None
        self.backend = Backend()
        self.channel = QWebChannel()
        self.channel.registerObject("backend", self.backend)

        self.pycon_canvas = None

        self.time = None
        self.lon_wgs84 = None
        self.lat_wgs84 = None

        self.geo_map = None

        self.__initUI()

    def __initUI(self):
        self.geo_map_view = QWebEngineView()
        self.geo_map_view.page().setWebChannel(self.channel)

        _layout = QVBoxLayout()
        _layout.addWidget(self.geo_map_view)

        self.win_widget = QWidget()
        self.win_widget.setLayout(_layout)
        self.setWidget(self.geo_map_view)

    def load(self, url):
        """
        USAGE
            self.win_widget.load(QUrl("http://qt-project.org/"))

            url = QtCore.QUrl.fromLocalFile(file_full_path)
            self.win_widget..load(url=url)
        """
        self.geo_map_view.load(url)

    def initialize(self):
        try:
            self.time = self.pycon_data_source.get_channel(channel_name="timestamp")
            self.lon_wgs84 = self.pycon_data_source.get_channel(channel_name="lon_wgs84")
            self.lat_wgs84 = self.pycon_data_source.get_channel(channel_name="lat_wgs84")
            self.set_status_ok()
            self.__render_geo_map()

            self.signal_time_loaded.emit(self.time.samples[0], self.time.samples[-1])
        except Exception as ex:
            logger().warning(str(ex))

    def __render_geo_map(self):
        try:
            self.geo_map = folium.Map(location=[48.8366488, 9.0966474], zoom_start=13)

            p_click = PyConFoliumClick()
            self.geo_map.add_child(p_click)

            self.data = io.BytesIO()
            self.geo_map.save(self.data, close_file=False)
            html = self.data.getvalue().decode()
            self.geo_map_view.setHtml(html)

        except Exception as e:
            logger().warning(f"{str(e)}")

    @QtCore.pyqtSlot(PyConTime)
    def slider_value_changed(self, time: PyConTime):
        if self.is_status_not_ok():
            return

        time_sec = time.get_time_sec()

        idx, t = find_nearest_time(arr=self.time.samples, value=time_sec)

        lon_wgs84 = self.lon_wgs84.samples[idx]
        lat_wgs84 = self.lat_wgs84.samples[idx]

        self.__add_marker(latitude=lat_wgs84, longitude=lon_wgs84)

    def __add_marker(self, latitude, longitude):
        # L.marker([{{latitude}}, {{longitude}}] ).addTo({{map}});
        template = Template(
            """
            pyConFoliumObjs.putMarker({{latitude}}, {{longitude}})
            """
        )

        js_code = template.render(latitude=latitude, longitude=longitude)
        self.geo_map_view.page().runJavaScript(js_code)
