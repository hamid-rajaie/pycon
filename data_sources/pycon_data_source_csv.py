import pandas as pd

from data_sources.pycon_data_source_csv_base import PyConDataSourceCsvBase


class PyConDataSourceCsv(PyConDataSourceCsvBase):
    def __init__(self, file_name: str):
        super().__init__()

        self.file_name = file_name
        self.__read_data()

    def __read_data(self):
        data_frame = pd.read_csv(self.file_name, index_col=None)
        self.set_data(data_frame=data_frame)

    def get_groups(self):
        return self.data.groups

    def get_channel(self, channel_name: str, group_index: int = None, channel_index: int = None):
        return self.data.get_the_channel(
            channel_name=channel_name, group_index=group_index, channel_index=channel_index
        )

    def get_channels(self):
        pass
