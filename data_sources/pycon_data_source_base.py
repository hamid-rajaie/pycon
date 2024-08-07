import re

from common.exceptions.exceptions import PyConSignalTimeSeriesNotFound
from common.logging.logger import logger
from pycon_config import get_pycon_config


class PyConDataSourceBase:

    class PyConSignal:
        def __init__(self) -> None:
            self.real_time_name = None
            self.real_time_series = None

            self.real_signal_name: str = None
            self.real_signal_series = None

            self.group_index: int = None
            self.plugin_names = []

    def __init__(self):
        self.data = None

        self.generic_to_real_map: dict = {}
        self.missing_needed_generic_signals_names: list = []
        self.missing_optional_generic_signals_names: list = []

        self.regex_indicator = "%"

        self.VIDEO_LINES_MAPPING = {
            "0": "left",
            "1": "right",
            "2": "leftLeft",
            "3": "rightRight",
            "4": "roadEdgeLeft",
            "5": "roadEdgeRight",
            "6": "roadEdgeLeftRaised",
            "7": "roadEdgeRightRaised",
        }

    def get_groups(self):
        raise Exception("get_groups is not implemented")

    def get_channel(self, channel_name: str, group_index: int = None, channel_index: int = None):
        raise Exception("get_channel is not implemented")

    def get_channels_names(self):
        raise Exception("get_channels is not implemented")

    def add_generic_signal(self, plugin_name, generic_signal_name: str):
        logger().info(f"[{plugin_name}] adds {generic_signal_name}")

        if generic_signal_name not in self.generic_to_real_map.keys():
            signal: PyConDataSourceBase.PyConSignal = PyConDataSourceBase.PyConSignal()
            signal.real_signal_name = generic_signal_name
            signal.plugin_names.append(plugin_name)
            self.generic_to_real_map[generic_signal_name] = signal
        else:
            signal: PyConDataSourceBase.PyConSignal = self.generic_to_real_map[generic_signal_name]
            signal.plugin_names.append(plugin_name)

    def get_channels(self):
        for generic_signal_name, signal in self.generic_to_real_map.items():

            try:
                signal.real_signal_series = self.get_channel(channel_name=signal.real_signal_name)

                try:
                    # ((data group index, channel index)(data group index, channel index)..)
                    _set_real = self.data.channels_db[signal.real_signal_name]

                    if len(_set_real) != 1:
                        for elem in _set_real:
                            group_index = elem[0]
                            _channel_index = elem[1]
                            logger().warning(f"group_index:{group_index}, channel_index:{_channel_index}")
                        raise Exception("more than one channels found")

                    signal.group_index = _set_real[0][0]
                    logger().info(f"group_index:{signal.group_index}, _channel_index:{signal._channel_index}")
                except AttributeError as ex:
                    signal.group_index = 0

                for sig_time in get_pycon_config().pycon_time_signals:
                    try:
                        signal.real_time_series = self.get_channel(
                            channel_name=sig_time, group_index=signal.group_index
                        )
                        signal.real_time_name = sig_time

                    except Exception:
                        # logger().warning(f"{sig_time} not found")
                        pass

                if signal.real_time_name is None or signal.real_time_series is None:
                    raise Exception("time not found")

            except Exception as ex:
                logger().warning(f"{type(ex)} {str(ex)}, plugins:{signal.plugin_names}")

    def get_real_signal_series(self, generic_channel_name):
        signal: PyConDataSourceBase.PyConSignal = self.generic_to_real_map[generic_channel_name]
        if signal.real_time_series is None or signal.real_signal_series is None:
            # logger().warning(f"time series not found for {generic_channel_name}")
            raise PyConSignalTimeSeriesNotFound(signal_name=generic_channel_name)

        return (signal.real_time_series, signal.real_signal_series)

    def __add_to_map(self, generic_signal_name: str, real_signal_name: str):

        signal: PyConDataSourceBase.PyConSignal = PyConDataSourceBase.PyConSignal()
        signal.real_signal_name = real_signal_name

        self.generic_to_real_map[generic_signal_name] = signal

    def missing_needed_generic_signals(self):
        return self.missing_needed_generic_signals_names

    def missing_optional_generic_signals(self):
        return self.missing_optional_generic_signals_names

    def setup_generic_real_map(self, yaml_data_dict: dict) -> tuple:

        # self.generic_to_real_map: dict = {}
        self.missing_needed_generic_signals_names: list = []
        self.missing_optional_generic_signals_names: list = []

        data_source_signal_names = self.get_channels_names()

        for generic_signal_name, real_signal_description in yaml_data_dict.items():

            try:
                real_signals = real_signal_description["signal"]

                real_optional = None
                if "optional" in real_signal_description.keys():
                    real_optional = real_signal_description["signal"]

                signal_available = False

                if isinstance(real_signals, list):

                    for _, real_signal_name in enumerate(real_signals):
                        if real_signal_name in data_source_signal_names:
                            if self.regex_indicator not in real_signal_name:
                                self.__add_to_map(
                                    generic_signal_name=generic_signal_name, real_signal_name=real_signal_name
                                )
                                signal_available = True
                                break
                        else:
                            if self.regex_indicator in real_signal_name:
                                regex_indices_alias = [
                                    i for i, c in enumerate(generic_signal_name) if c == self.regex_indicator
                                ]
                                regex_indices_signal = [
                                    i for i, c in enumerate(real_signal_name) if c == self.regex_indicator
                                ]
                                regex_pattern = re.escape(
                                    real_signal_name[: regex_indices_signal[0]]
                                )  # add the initial part of the string
                                for i, index in enumerate(regex_indices_signal):
                                    if i == 0:
                                        continue  # skip the first occurrence since it was already added
                                    prev_index = regex_indices_signal[i - 1]
                                    regex_pattern += r"(?P<index{}_>\d+)".format(i)  # add the named capturing group
                                    regex_pattern += re.escape(
                                        real_signal_name[prev_index + 1 : index]
                                    )  # add the text between the % and the next occurrence
                                regex_pattern += r"(?P<index{}_>\d+)".format(
                                    len(regex_indices_signal)
                                )  # add the final named capturing group
                                regex_pattern += re.escape(
                                    real_signal_name[regex_indices_signal[-1] + 1 :]
                                )  # add the final part of the string

                                # find all matches
                                matches = re.findall(regex_pattern, str(data_source_signal_names))
                                if matches:
                                    for match in matches:
                                        if not isinstance(match, tuple):
                                            match = [match]
                                        new_generic_signal_name = generic_signal_name
                                        new_signal = real_signal_name
                                        for pos, index in enumerate(match):
                                            new_generic_signal_name = (
                                                new_generic_signal_name[: regex_indices_alias[pos]]
                                                + index
                                                + new_generic_signal_name[regex_indices_alias[pos] + 1 :]
                                            )
                                            new_signal = (
                                                new_signal[: regex_indices_signal[pos]]
                                                + index
                                                + new_signal[regex_indices_signal[pos] + 1 :]
                                            )
                                        # for videoLines we need to map the generic_signal_name name back!
                                        if (
                                            "videoLines" in new_generic_signal_name
                                            and "polynomialLine" not in new_generic_signal_name
                                        ):
                                            # index:    11 12
                                            # videoLines.X.
                                            new_generic_signal_name = (
                                                new_generic_signal_name[:11]
                                                + self.VIDEO_LINES_MAPPING.get(
                                                    match[0], f"UNKOWN-{new_generic_signal_name[11]}"
                                                )
                                                + new_generic_signal_name[12:]
                                            )
                                        self.__add_to_map(
                                            generic_signal_name=new_generic_signal_name, real_signal_name=new_signal
                                        )

                                        signal_available = True

                                if signal_available:
                                    break
                if not signal_available and real_optional is not None:
                    self.missing_needed_generic_signals_names.append(generic_signal_name)
                if not signal_available and real_optional is None:
                    self.missing_optional_generic_signals_names.append(generic_signal_name)
            except Exception as exp:
                logger().warning(f"generic_signal_name: {generic_signal_name}  {str(exp)}")
