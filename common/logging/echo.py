import sys
from enum import Enum

import click


class _LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


_LEVEL_COLOR_MAP = {
    _LogLevel.DEBUG: "cyan",
    _LogLevel.INFO: "bright_blue",
    _LogLevel.WARNING: "yellow",
    _LogLevel.ERROR: "red",
    _LogLevel.CRITICAL: "bright_red",
}


def __disable_echos() -> bool:
    return any(arg in sys.argv for arg in ["test", "migrate", "makemigrations", "createsuperuser"])


def __echo(level: _LogLevel, message: str) -> None:
    if __disable_echos():
        return

    # Get the color for the given level
    fg = _LEVEL_COLOR_MAP[level]

    # Find the longest level string among all defined echo functions
    max_level_length = max(len(level.name) for level in _LogLevel)

    # Calculate the number of spaces needed for alignment
    num_spaces = max_level_length - len(level.name)

    # Print the formatted message with calculated spaces
    click.echo(f"{click.style(level.name, fg=fg)}{' '*num_spaces} | {message}")


def echo_debug(message: str) -> None:
    __echo(level=_LogLevel.DEBUG, message=message)


def echo_info(message: str) -> None:
    __echo(level=_LogLevel.INFO, message=message)


def echo_warning(message: str) -> None:
    __echo(level=_LogLevel.WARNING, message=message)


def echo_error(message: str) -> None:
    __echo(level=_LogLevel.ERROR, message=message)


def echo_critical(message: str) -> None:
    __echo(level=_LogLevel.CRITICAL, message=message)
