import os

from data_sources.pycon_data_source import PyConDataSource


class PyConPluginParams:
    def __init__(self, selected_file_name: str, pycon_data_source: PyConDataSource) -> None:

        self.pycon_data_source: PyConDataSource = pycon_data_source

        self.video_name = os.path.join(
            os.path.dirname(selected_file_name),
            os.path.splitext(os.path.basename(selected_file_name))[0] + ".mp4",
        )
