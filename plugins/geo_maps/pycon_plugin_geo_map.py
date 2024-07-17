import io
import traceback

import folium
from jinja2 import Template
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QAction, QMenu

from common.exceptions.exceptions import PyConSignalTimeSeriesNotFound
from common.logging.logger import logger
from common.plugins.pycon_plugin_base import PyConPluginBase
from common.plugins.pycon_plugin_params import PyConPluginParams
from common.pycon_numpy import find_nearest_time
from data_sources.pycon_data_source_base import PyConDataSourceBase
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

    def __init__(self, params: PyConPluginParams):
        super().__init__()

        self.pycon_data_source: PyConDataSourceBase = params.pycon_data_source

        self.setWindowTitle("Geo Map")

        self.geo_map_view = None
        self.backend = Backend()
        self.channel = QWebChannel()
        self.channel.registerObject("backend", self.backend)

        self.pycon_canvas = None
        self.geo_map = None

        self.__initUI()

    def add_generic_signals(self):
        # self.pycon_data_source.add_generic_signal(plugin_name=self.windowTitle(), generic_signal_name="timestamp")
        self.pycon_data_source.add_generic_signal(plugin_name=self.windowTitle(), generic_signal_name="lon_wgs84")
        self.pycon_data_source.add_generic_signal(plugin_name=self.windowTitle(), generic_signal_name="lat_wgs84")

    def __initUI(self):
        self.geo_map_view = QWebEngineView()
        self.geo_map_view.page().setWebChannel(self.channel)

        super().initUI(widget=self.geo_map_view, with_menubar=True)

        menu_needed_signals = QMenu("&Needed Signals", self)
        self.menubar().addMenu(menu_needed_signals)

        # for signal in self.get_generic_names():
        #    action_signal = QAction(signal, self)
        #    menu_needed_signals.addAction(action_signal)

    def initPlugin(self):
        try:
            self.__render_geo_map()

        except PyConSignalTimeSeriesNotFound as ex:
            logger().warning(str(ex))
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
            pass

        time_sec = time.get_time_sec()

        try:

            (time_lon_series, lon_wgs84_series) = self.pycon_data_source.get_real_signal_series(
                generic_channel_name="lon_wgs84"
            )
            (time_lat_series, lat_wgs84_series) = self.pycon_data_source.get_real_signal_series(
                generic_channel_name="lat_wgs84"
            )

            idx, t = find_nearest_time(arr=time_lon_series.samples, value=time_sec)

            lon_wgs84 = lon_wgs84_series.samples[idx]
            lat_wgs84 = lat_wgs84_series.samples[idx]

            self.__add_marker(latitude=lat_wgs84, longitude=lon_wgs84)
        except Exception as ex:
            logger().warning("putting marker on the map not possible")
            # logger().error(f"{traceback.print_exception(type(ex), ex, ex.__traceback__)}")

    def __add_marker(self, latitude, longitude):
        # L.marker([{{latitude}}, {{longitude}}] ).addTo({{map}});
        template = Template(
            """
            pyConFoliumObjs.putMarker({{latitude}}, {{longitude}})
            """
        )

        js_code = template.render(latitude=latitude, longitude=longitude)
        self.geo_map_view.page().runJavaScript(js_code)
