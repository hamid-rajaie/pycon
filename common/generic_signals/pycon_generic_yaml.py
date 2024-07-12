import os
import re

import numpy as np
import yaml

from common.logging.logger import logger
from data_sources.pycon_data_source_base import PyConDataSourceBase
from pycon_config import get_pycon_config


class PyConGenericYaml:

    def __init__(self, pycon_data_source: PyConDataSourceBase):

        self.pycon_data_source = pycon_data_source

        self.alias_signal_dict: dict = {}
        self.missing_needed_signals: list = []
        self.missing_optional_signals: list = []

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

    def open_yaml_file(self, yaml_file):

        with open(yaml_file, "r") as file:
            yaml_data_dict = yaml.safe_load(file)
            self.parse_yaml(yaml_data_dict=yaml_data_dict)

    def parse_yaml(self, yaml_data_dict: dict) -> tuple:

        self.alias_signal_dict = {}
        self.missing_needed_signals = []
        self.missing_optional_signals = []

        data_mf4 = self.pycon_data_source.data
        iter_mf4 = data_mf4.channels_db.keys()
        signals_mf4 = [channel.name for group in data_mf4.groups for channel in group.channels]

        for generic_signal_name, real_signal_description in yaml_data_dict.items():

            try:
                real_signals = real_signal_description["signal"]

                real_optional = None
                if "optional" in real_signal_description.keys():
                    real_optional = real_signal_description["signal"]

                signal_available = False

                if isinstance(real_signals, list):

                    for _, real_signal in enumerate(real_signals):
                        if real_signal in iter_mf4:
                            if self.regex_indicator not in real_signal:
                                self.alias_signal_dict[generic_signal_name] = real_signal
                                signal_available = True
                                break
                        else:
                            if self.regex_indicator in real_signal:
                                regex_indices_alias = [
                                    i for i, c in enumerate(generic_signal_name) if c == self.regex_indicator
                                ]
                                regex_indices_signal = [
                                    i for i, c in enumerate(real_signal) if c == self.regex_indicator
                                ]
                                regex_pattern = re.escape(
                                    real_signal[: regex_indices_signal[0]]
                                )  # add the initial part of the string
                                for i, index in enumerate(regex_indices_signal):
                                    if i == 0:
                                        continue  # skip the first occurrence since it was already added
                                    prev_index = regex_indices_signal[i - 1]
                                    regex_pattern += r"(?P<index{}_>\d+)".format(i)  # add the named capturing group
                                    regex_pattern += re.escape(
                                        real_signal[prev_index + 1 : index]
                                    )  # add the text between the % and the next occurrence
                                regex_pattern += r"(?P<index{}_>\d+)".format(
                                    len(regex_indices_signal)
                                )  # add the final named capturing group
                                regex_pattern += re.escape(
                                    real_signal[regex_indices_signal[-1] + 1 :]
                                )  # add the final part of the string

                                # find all matches
                                matches = re.findall(regex_pattern, str(signals_mf4))
                                if matches:
                                    for match in matches:
                                        if not isinstance(match, tuple):
                                            match = [match]
                                        new_alias = generic_signal_name
                                        new_signal = real_signal
                                        for pos, index in enumerate(match):
                                            new_alias = (
                                                new_alias[: regex_indices_alias[pos]]
                                                + index
                                                + new_alias[regex_indices_alias[pos] + 1 :]
                                            )
                                            new_signal = (
                                                new_signal[: regex_indices_signal[pos]]
                                                + index
                                                + new_signal[regex_indices_signal[pos] + 1 :]
                                            )
                                        # for videoLines we need to map the generic_signal_name name back!
                                        if "videoLines" in new_alias and "polynomialLine" not in new_alias:
                                            # index:    11 12
                                            # videoLines.X.
                                            new_alias = (
                                                new_alias[:11]
                                                + self.VIDEO_LINES_MAPPING.get(match[0], f"UNKOWN-{new_alias[11]}")
                                                + new_alias[12:]
                                            )
                                        self.alias_signal_dict[new_alias] = new_signal
                                        signal_available = True

                                if signal_available:
                                    break
                if not signal_available and real_optional is not None:
                    self.missing_optional_signals.append(generic_signal_name)
                if not signal_available and real_optional is None:
                    self.missing_needed_signals.append(generic_signal_name)
            except Exception as exp:
                logger().warning(f"generic_signal_name: {generic_signal_name}  {str(exp)}")

    # ==========================================================================
    # search
    # ==========================================================================
    def slot_timer_timeout(self):
        logger().info("timeout ... render result")
        self.timer.stop()
        self.timer_started = False

        self.add_alias_signals()

    def slot_search(self, search_text):
        logger().info(f"{search_text} ... {self.search_cnt}")

        self.search_text = search_text
        self.search_cnt = self.search_cnt + 1

        if not self.timer_started:
            self.timer.start(self.search_time_out)
            self.timer_started = True
        else:
            self.timer.stop()
            self.timer.start(self.search_time_out)
            self.timer_started = True
        return
