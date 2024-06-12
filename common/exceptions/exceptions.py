import os
from typing import List


class PyConException(Exception):
    """Base error for the application."""

    def __init__(self, msg: str, additional_info: List[str] = None):
        modified_msg = msg
        if additional_info:
            modified_msg += " (" + " ".join(additional_info) + ")"

        super().__init__(modified_msg)


class PyConSignalNotFound(PyConException):
    def __init__(self, signal_name: str):
        msg = "SignalNotFound"
        super().__init__(msg)
        self.signal_name = signal_name
