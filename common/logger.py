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
        handlers.append(setup_logger_stream(formatter))
    else:
        handlers.append(setup_logger_file(formatter, filename))
        handlers.append(setup_logger_stream(formatter))

    logger.setLevel(level)
    for handler in handlers:
        logger.addHandler(handler)


# # sys.stdout mainly for debugging purposes
def setup_logger_stream(formatter):
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setFormatter(formatter)
    return sh


def setup_logger_file(formatter, filename):
    fh = logging.FileHandler(filename)
    fh.setFormatter(formatter)
    return fh


def get_logger():
    global logger
    return logger