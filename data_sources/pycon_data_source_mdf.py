import time

from asammdf import MDF

from common.logging.logger import logger
from data_sources.pycon_data_source_base import PyConDataSourceBase


class PyConDataSourceMdf(PyConDataSourceBase):
    def __init__(self, file_name: str):
        super().__init__()

        self.file_name = file_name

        self.__read_data()

    def __read_data(self):
        # TODO when should I close the file
        t1 = time.time()
        logger().info("opening mdf file ...")
        self.data = MDF(self.file_name, memory="minimum")
        t2 = time.time()
        logger().info(f"open mdf file took {(t2-t1):.2f} sec")

        logger().info("mdf file is opened ... ")
        self.iter_mdf = self.data.channels_db.keys()
        logger().info((f"len(self.iter_mdf) : {len(self.iter_mdf)}"))

    def get_groups(self):
        return self.data.groups

    def get_channel(self, channel_name: str, group_index: int = None, channel_index: int = None):
        # logger().info(f"channel_name:{channel_name}  group_index:{group_index}  channel_index:{channel_index}")
        return self.data.get(channel_name, group_index, channel_index)

    def get_channels_names(self):
        channel_names = [channel.name for group in self.data.groups for channel in group.channels]
        return channel_names

    def get_channels_names_v2(self):
        return self.data.channels_db.keys()
