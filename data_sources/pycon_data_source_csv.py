import pandas as pd

from data_sources.pycon_data_source import PyConDataSource
from data_sources.pycon_data_source_interface import (
    PyConDataSourceChannel,
    PyConDataSourceChannelGroup,
    PyConDataSourceChannelSignal,
    PyConDataSourceGroup,
    PyConDataSourceGroups,
)


class PyConDataSourceCsv(PyConDataSource):
    def __init__(self, file_name: str):
        super().__init__()

        self.file_name = file_name
        self.data_frame = None
        self.__read_data()

    def __read_data(self):
        self.data_frame = pd.read_csv(self.file_name, index_col=None)

        channel_group = PyConDataSourceChannelGroup(comment="main group")

        group = PyConDataSourceGroup(channel_group=channel_group)

        for col in self.data_frame.columns:
            samples = self.data_frame[col].to_numpy()
            signal = PyConDataSourceChannelSignal(samples=samples)
            channel = PyConDataSourceChannel(name=col, signal=signal)

            group.channels.append(channel)

        self.data = PyConDataSourceGroups()
        self.data.groups.append(group)

    def get_groups(self):
        return self.data.groups

    def get_channel(self, channel_name: str, group_index: int = None, channel_index: int = None):
        return self.data.get_the_channel(
            channel_name=channel_name, group_index=group_index, channel_index=channel_index
        )
