import pandas as pd

from common.logging.logger import logger
from data_sources.pycon_data_source_base import PyConDataSourceBase


class PyConDataSourceChannelSignal:
    def __init__(self, samples) -> None:
        self.samples = samples


class PyConDataSourceChannel:
    def __init__(self, name: str, signal: PyConDataSourceChannelSignal) -> None:
        self.name: str = name
        self.signal: PyConDataSourceChannelSignal = signal


class PyConDataSourceChannelGroup:
    def __init__(self, comment: str) -> None:
        self.comment: str = comment


class PyConDataSourceGroup:
    def __init__(self, channel_group: PyConDataSourceChannelGroup) -> None:
        self.channel_group: PyConDataSourceChannelGroup = channel_group
        self.channels: list[PyConDataSourceChannel] = []


class PyConDataSourceGroups:
    def __init__(self) -> None:
        self.groups: list[PyConDataSourceGroup] = []

    def get_the_channel(self, channel_name: str, group_index: int = None, channel_index: int = None):
        logger().info(f"channel_name:{channel_name} group_index:{group_index} channel_index:{channel_index}")

        if group_index is not None and channel_index is not None:
            channel = self.groups[group_index].channels[channel_index]

            if channel.name == channel_name:
                return channel.signal
            else:
                raise Exception("channel not found")
        else:
            found_channels = []
            for group in self.groups:
                for channel in group.channels:
                    if channel.name == channel_name:
                        found_channels.append(channel)

            if len(found_channels) == 0:
                raise Exception(f"No channel:{channel_name} found")
            elif len(found_channels) == 1:
                return found_channels[0].signal
            else:
                raise Exception(
                    f"Multiple occurrences for channel :{channel_name} found, Provide both group and index arguments to select another data group"
                )


class PyConDataSourceCsvBase(PyConDataSourceBase):

    def __init__(self) -> None:
        self.data = PyConDataSourceGroups()

    def set_data(self, data_frame: pd.DataFrame):
        channel_group = PyConDataSourceChannelGroup(comment="main group")

        group = PyConDataSourceGroup(channel_group=channel_group)

        for col in data_frame.columns:
            samples = data_frame[col].to_numpy()
            signal = PyConDataSourceChannelSignal(samples=samples)
            channel = PyConDataSourceChannel(name=col, signal=signal)

            group.channels.append(channel)

        # self.data = PyConDataSourceGroups()
        self.data.groups.append(group)
