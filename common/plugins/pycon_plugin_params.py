import os

from data_sources.pycon_data_source_base import PyConDataSourceBase


class PyConPluginParams:

    def __init__(self, selected_file_name: str, pycon_data_source: PyConDataSourceBase, initial_yaml_dir: str) -> None:

        self.pycon_data_source: PyConDataSourceBase = pycon_data_source

        # self.alias_signal_dict = {}

        self.initial_yaml_dir = ""

        self.video_name = os.path.join(
            os.path.dirname(selected_file_name),
            os.path.splitext(os.path.basename(selected_file_name))[0] + ".mp4",
        )
