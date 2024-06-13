from enum import Enum

from pycon_config import get_pycon_config


class PyConTime(object):

    class PyConTimeUnit(Enum):
        M_SEC = "msec"
        SEC = "sec"

    def __init__(self, time: int, time_diff: int, unit: PyConTimeUnit) -> None:
        self.time = time
        self.time_diff = time_diff
        self.unit = unit

    def get_time_sec(self):
        if self.unit == PyConTime.PyConTimeUnit.SEC:
            return self.time
        elif self.unit == PyConTime.PyConTimeUnit.M_SEC:
            return self.time / 1000
        else:
            raise Exception(f"unsupported time unit : {self.unit}")

    def get_time_msec(self):
        if self.unit == PyConTime.PyConTimeUnit.SEC:
            return self.time * 1000
        elif self.unit == PyConTime.PyConTimeUnit.M_SEC:
            return self.time
        else:
            raise Exception(f"unsupported time unit : {self.unit}")

    def get_time_diff_sec(self):
        if self.unit == PyConTime.PyConTimeUnit.SEC:
            return self.time_diff
        elif self.unit == PyConTime.PyConTimeUnit.M_SEC:
            return self.time_diff / 1000
        else:
            raise Exception(f"unsupported time unit : {self.unit}")

    def get_time_diff_msec(self):
        if self.unit == PyConTime.PyConTimeUnit.SEC:
            return self.time_diff * 1000
        elif self.unit == PyConTime.PyConTimeUnit.M_SEC:
            return self.time_diff
        else:
            raise Exception(f"unsupported time unit : {self.unit}")
