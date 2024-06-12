import atexit
import inspect
import logging
import logging.config
import os
import sys
import time

import click

from common.logging.config import LOGGING_CONFIG
from common.logging.echo import echo_warning
from pycon_config import get_pycon_config


class MyLogger:
    def __init__(self, messages: list = []):
        self.messages = messages

        self.stdout = None
        self.stderr = None

        logging.config.dictConfig(LOGGING_CONFIG)

        self.logger: logging.Logger = logging.getLogger("")

    def debug(self, message: str, caller_index: int = 3, show_meta_info: bool = True):
        self.log(message, func=self.logger.debug, caller_index=caller_index, show_meta_info=show_meta_info)

    def api(self, message: str, caller_index: int = 3, show_meta_info: bool = True):
        self.log(message, func=self.logger.api, caller_index=caller_index, show_meta_info=show_meta_info)

    def info(self, message: str, caller_index: int = 3, show_meta_info: bool = True):
        self.log(message, func=self.logger.info, caller_index=caller_index, show_meta_info=show_meta_info)

    def warning(self, message: str, caller_index: int = 3, show_meta_info: bool = True):
        self.log(message, func=self.logger.warning, caller_index=caller_index, show_meta_info=show_meta_info)

    def error(self, message: str, caller_index: int = 3, show_meta_info: bool = True):
        self.log(message, func=self.logger.error, caller_index=caller_index, show_meta_info=show_meta_info)

    def critical(self, message: str, caller_index: int = 3, show_meta_info: bool = True):
        self.log(message, func=self.logger.critical, caller_index=caller_index, show_meta_info=show_meta_info)

    def info_detail(self, thread_id, message: str):
        message = f"[Thread ID: {thread_id}] {message}"
        self.info(message)

    def log(self, message: str, func: callable, caller_index: int = 3, show_meta_info: bool = True):
        meta_info = self.get_file_info(caller_index) if show_meta_info else None
        self.messages.append({"message": f"{message}", "function": func, "fileinfo": meta_info})

        self.run()

    def get_file_info(self, caller_index: int = 3):
        stack = inspect.stack()
        frame_info_caller = stack[caller_index]
        caller_info = inspect.getframeinfo(frame_info_caller[0])

        filename = frame_info_caller.filename
        lineno = caller_info.lineno

        function = None

        if "self" in frame_info_caller[0].f_locals.keys():
            function = frame_info_caller[0].f_code.co_name
        else:
            function = frame_info_caller.function

        fileinfo = f"{filename}:{lineno}"

        if function:
            fileinfo = f"{fileinfo} | {click.style(function,fg='yellow')}"

        return fileinfo

    def run(self):
        while len(self.messages) > 0:
            logItem = self.messages.pop(0)

            func: callable = logItem["function"]
            msg: str = logItem["message"]

            extra = {}

            fileinfo: str = logItem["fileinfo"]
            if fileinfo:
                extra.update({"fileinfo": fileinfo})

            verbose_logging = get_pycon_config().verbose_logging
            if verbose_logging:
                for key, value in verbose_logging.items():
                    extra.update({key: value})

            # extra is a standard argument for the logging functions and
            # is used to pass additional information to the logging
            # formatter.
            func(msg, extra=extra)

    def atexit(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr

        self.info("PyCon Logger has been deleted.", show_meta_info=False)

        time.sleep(2)


def create_stream_to_logger_redirector(stream_name, log_method, filter=None):
    class StreamToLoggerRedirector(object):
        def __init__(self, logger: MyLogger):
            self.logger: MyLogger = logger

        def write(self, buf):
            if filter and buf in filter:
                return

            styled_stream_name = click.style(
                stream_name,
                fg="blue" if stream_name == "sys.stdout" else "bright_red",
            )
            func = getattr(self.logger, log_method)

            for line in buf.rstrip().splitlines():
                func(message=f"{styled_stream_name} {line}", caller_index=2, show_meta_info=False)

        def flush(self):
            pass

    return StreamToLoggerRedirector


StdOutToLoggerRedirector = create_stream_to_logger_redirector("sys.stdout", "info")
StdErrToLoggerRedirector = create_stream_to_logger_redirector("sys.stderr", "error")


LOGGER = None


def try_to_remove_old_log_file(log_file_path: os.PathLike) -> None:
    try:
        os.remove(log_file_path)
    except FileNotFoundError:
        pass
    except PermissionError:
        echo_warning(f"PermissionError: Could not delete {log_file_path}")
        pass
    except Exception as ex:
        echo_warning(f"{str(ex)}")
        pass


def logger():
    global LOGGER
    if LOGGER is None:
        if get_pycon_config().delete_old_log_at_startup:
            try_to_remove_old_log_file(get_pycon_config().log_file)

        LOGGER = MyLogger()

        LOGGER.stdout = sys.stdout
        LOGGER.stderr = sys.stderr

        sys.stdout = StdOutToLoggerRedirector(LOGGER)
        sys.stderr = StdErrToLoggerRedirector(LOGGER)

        #! This is required to prevent the logger from crashing when the
        #! output is not a terminal, e.g. when using Celery.
        sys.stdout.isatty = lambda: False
        sys.stdout.encoding = sys.getdefaultencoding()

        sys.stderr.isatty = lambda: False
        sys.stderr.encoding = sys.getdefaultencoding()

        atexit.register(LOGGER.atexit)

        LOGGER.info("PyCon Logger has been created.", show_meta_info=False)

    return LOGGER
