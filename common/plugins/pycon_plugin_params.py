import os

from PyQt5.QtWidgets import QMdiArea, QWidget

from data_sources.pycon_data_source import PyConDataSource


class PyConPluginParams:
    def __init__(
        self, selected_file_name: str, tab: QWidget, tab_mdi_area: QMdiArea, pycon_app_data_source: PyConDataSource
    ) -> None:
        self.selected_file_name: str = selected_file_name
        self.tab: QWidget = tab
        self.tab_mdi_area: QMdiArea = tab_mdi_area
        self.pycon_app_data_source: PyConDataSource = pycon_app_data_source

        self.video_name = os.path.join(
            os.path.dirname(selected_file_name),
            os.path.splitext(os.path.basename(selected_file_name))[0] + ".mp4",
        )
