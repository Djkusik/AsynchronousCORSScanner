import logging
import logging.handlers
import sys

global logger

def log_level(val):
    return {
        1: logging.CRITICAL,
        2: logging.ERROR,
        3: logging.WARNING,
        4: logging.INFO,
        5: logging.DEBUG
    }.get(val, 4)


def setup_logger(level=logging.INFO, filename=None):
    global logger
    logger = logging.getLogger('cors')
    formatter = logging.Formatter('%(asctime)s::%(levelname)s:: %(message)s')
    handlers = []

    if filename is None:
        handlers.append(setup_logger_stream(formatter, level))
    else:
        handlers.append(setup_logger_file(formatter, level, filename))
        handlers.append(setup_logger_stream(formatter, level))

    logger.setLevel(level)
    for handler in handlers:
        logger.addHandler(handler)


# # sys.stdout mainly for debugging purposes
def setup_logger_stream(formatter, level):
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setFormatter(formatter)
    sh.setLevel(level)
    return sh


def setup_logger_file(formatter, level, filename):
    fh = logging.FileHandler(filename)
    fh.setFormatter(formatter)
    fh.setLevel(level)
    return fh


def get_logger():
    global logger
    return logger