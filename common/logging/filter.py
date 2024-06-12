import logging
from typing import Union


class NonErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> Union[bool, logging.LogRecord]:
        return record.levelno <= logging.INFO
