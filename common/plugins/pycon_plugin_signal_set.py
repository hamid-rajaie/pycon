from common.logging.logger import logger
from common.plugins.pycon_plugin_state import PyConPluginState


class PyConSignal:
    def __init__(self) -> None:
        self.channel_name: str = None
        self.channel = None


class PyConPluginSignalSet(PyConPluginState):
    def __init__(self) -> None:
        #
        # {
        #    "generic_name_1" : PyConSignal(),
        #    "generic_name_2" : PyConSignal(),
        # }
        #
        self.__dict = {}

    def add_generic_channel(self, generic_signal: str):
        signal: PyConSignal = PyConSignal()
        signal.channel_name = generic_signal

        self.__dict[generic_signal] = signal

    def get_generic_channel(self, generic_signal) -> dict:

        signal: PyConSignal = self.__dict[generic_signal]
        return signal.channel

    def get_generic_names(self) -> list[str]:
        return self.__dict.keys()

    def read_generic_channels(self):
        self.set_status_ok()
        for generic_name in self.__dict.keys():
            try:
                signal: PyConSignal = self.__dict[generic_name]
                signal.channel = self.pycon_data_source.get_channel(channel_name=signal.channel_name)

            except Exception as ex:
                logger().warning(str(ex))
                self.set_status_not_ok()
