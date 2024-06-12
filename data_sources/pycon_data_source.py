class PyConDataSource:
    def __init__(self):
        self.pycon_app_data = None

    def get_groups(self):
        raise Exception("get_groups is not implemented")

    def get_channel(self, channel_name: str, group_index: int = None, channel_index: int = None):
        return Exception("get_channel is not implemented")
