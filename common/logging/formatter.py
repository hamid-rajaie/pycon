import logging
import sys
from copy import copy
from typing import Literal, Union

import click

from pycon_config import get_pycon_config

# This har coded value is based on the current status of python logging lib
# logging.INFO = 20
# logging.DEBUG = 10
API_LOG_LEVEL = 20


class TerminalFormatter(logging.Formatter):
    """
    A custom log formatter class that  Outputs the LOG_LEVEL with an
    appropriate color.
    """

    level_name_colors = {
        # API_LOG_LEVEL: lambda level_name: click.style(str(level_name), fg="magenta"),
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="cyan"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="bright_blue"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(str(level_name), fg="bright_red"),
    }

    def __init__(
        self,
        fmt: Union[str, None] = None,
        datefmt: Union[str, None] = None,
        style: Literal["%", "{", "$"] = "%",
        level_colors: Union[bool, None] = None,
        message_colors: Union[bool, None] = None,
    ):
        def use_color(flag: Union[bool, None]) -> bool:
            if flag in (True, False):
                return flag
            return sys.stdout.isatty()

        self.level_colors = use_color(level_colors)
        self.message_colors = use_color(message_colors)
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def colorize(self, item: str, level_no: int) -> str:
        def default(level_name: str) -> str:
            return str(level_name)

        func = self.level_name_colors.get(level_no, default)
        return func(item)

    def verbosify(self, message: str, record: logging.LogRecord) -> str:
        msg = copy(message)
        # The fileinfo has to be passed from the outside because the logger
        # thread collects all messages first and then logs them. If we would
        # call the stack from here we would only be able to access the thread
        # and not the original log caller.
        if "fileinfo" in record.__dict__:
            msg = f"{msg} | {record.__dict__['fileinfo']}"
        if "log_process" in record.__dict__ and record.__dict__["log_process"]:
            msg = f"{msg} | {click.style(record.processName,fg='yellow')}: {record.process}"
        if "log_thread" in record.__dict__ and record.__dict__["log_thread"]:
            msg = f"{msg} | {click.style(record.threadName,fg='yellow')}: {record.thread}"
        return msg

    def formatMessage(self, record: logging.LogRecord) -> str:
        recordcopy = copy(record)
        levelname = recordcopy.levelname
        message = recordcopy.getMessage()
        separator = " " * (8 - len(recordcopy.levelname))
        if get_pycon_config().log_api_prefix:  # and recordcopy.levelno == API_LOG_LEVEL:
            message = f"PyCon API | {message}"
        if self.level_colors:
            levelname = self.colorize(levelname, recordcopy.levelno)
        if self.message_colors:
            message = self.colorize(message, recordcopy.levelno)
        message = self.verbosify(message=message, record=recordcopy)
        # clear colors from verbosify
        if not self.message_colors:
            message = click.unstyle(message)
        recordcopy.__dict__["levelname"] = levelname + separator
        recordcopy.__dict__["message"] = message
        return super().formatMessage(recordcopy)


class FileFormatter(TerminalFormatter):
    def __init__(
        self,
        fmt: Union[str, None] = None,
        datefmt: Union[str, None] = None,
        style: Literal["%", "{", "$"] = "%",
    ):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, level_colors=False, message_colors=False)

    def formatMessage(self, record: logging.LogRecord) -> str:
        return click.unstyle(super().formatMessage(record=record))
