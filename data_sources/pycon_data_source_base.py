class PyConDataSourceBase:
    def __init__(self):
        self.data = None

    def get_groups(self):
        raise Exception("get_groups is not implemented")

    def get_channel(self, channel_name: str, group_index: int = None, channel_index: int = None):
        return Exception("get_channel is not implemented")

    def get_channels(self):
        return Exception("get_channels is not implemented")
