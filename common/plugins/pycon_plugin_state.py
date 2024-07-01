from enum import Enum


class PyConStatus(Enum):
    OK = "ok"
    NOT_OK = "not_ok"


class PyConPluginState:

    def __init__(self) -> None:
        self.status: PyConStatus = PyConStatus.NOT_OK

    def set_status_ok(self):
        self.status = PyConStatus.OK

    def set_status_not_ok(self):
        self.status = PyConStatus.NOT_OK

    def is_status_ok(self):
        if self.status == PyConStatus.OK:
            return True
        return False

    def is_status_not_ok(self):
        if self.status == PyConStatus.NOT_OK:
            return True
        return False
