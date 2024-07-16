import re

from common.logging.logger import logger


class PyConDataSourceBase:

    class PyConSignal:
        def __init__(self) -> None:
            self.real_signal_name: str = None
            self.time_series = None

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
        return Exception("get_channel is not implemented")

    def get_channels_names(self):
        return Exception("get_channels is not implemented")

    def add_to_map(self, generic_signal_name, real_signal_name):

        signal: PyConDataSourceBase.PyConSignal = PyConDataSourceBase.PyConSignal()
        signal.real_signal_name = real_signal_name

        self.generic_to_real_map[generic_signal_name] = signal

    def missing_needed_generic_signals(self):
        return self.missing_needed_generic_signals_names

    def missing_optional_generic_signals(self):
        return self.missing_optional_generic_signals_names

    def setup_generic_real_map(self, yaml_data_dict: dict) -> tuple:

        self.generic_to_real_map: dict = {}
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
                                self.add_to_map(
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
                                        self.add_to_map(
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
