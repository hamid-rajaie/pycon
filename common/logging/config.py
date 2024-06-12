import logging

from pycon_config import get_pycon_config

FMT = "%(levelname)-8s | %(asctime)s | %(message)s"

DATEFMT = "%Y.%m.%d %H:%M:%S"

PYCON_LOG_LEVEL = get_pycon_config().pycon_log_level

PYCON_LOGGING_HANDLERS = get_pycon_config().logging_handlers


LOGGING_CONFIG: dict[str, any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "terminal": {
            "()": "common.logging.formatter.TerminalFormatter",
            "fmt": FMT,
            "datefmt": DATEFMT,
        },
        "file": {
            "()": "common.logging.formatter.FileFormatter",
            "fmt": FMT,
            "datefmt": DATEFMT,
        },
    },
    "handlers": {
        "terminal": {
            "class": "logging.StreamHandler",
            "level": PYCON_LOG_LEVEL,
            "formatter": "terminal",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": PYCON_LOG_LEVEL,
            "formatter": "file",
            "filename": get_pycon_config().log_file,
            "when": "midnight",
            "backupCount": 10,
        },
    },
    "loggers": {
        "": {
            "handlers": PYCON_LOGGING_HANDLERS,
            "level": PYCON_LOG_LEVEL,
            "propagate": True,
        },
    },
}
