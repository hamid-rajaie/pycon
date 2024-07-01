from common.plugins.pycon_state import PyConState


class PyConSignal:
    def __init__(self) -> None:
        self.channel_name: str = None
        self.channel = None


class PyConGenericSignalSet(PyConState):
    def __init__(self) -> None:
        #
        # {
        #    "generic_name_1" : PyConSignal(),
        #    "generic_name_2" : PyConSignal(),
        # }
        #
        self.__dict = {}

    def add_generic_channel(self, generic_signal: str):
        self.__dict[generic_signal] = PyConSignal()

    def get_generic_channel(self, generic_signal) -> dict:

        signal: PyConSignal = self.__dict[generic_signal]
        return signal.channel

    def get_generic_names(self) -> list[str]:
        return self.__dict.keys()

    def read_plugin_channels(self):
        self.set_status_ok()
        for generic_name in self.__dict.keys():
            try:
                signal: PyConSignal = self.__dict[generic_name]
                signal.channel = self.pycon_data_source.get_channel(channel_name=generic_name)

            except Exception as ex:
                logger().warning(str(ex))
                self.set_status_not_ok()
