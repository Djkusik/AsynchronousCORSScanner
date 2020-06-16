import logging
import logging.handlers
import sys

from multiprocessing_logging import install_mp_handler

def log_level(val):
    return {
        1: logging.CRITICAL,
        2: logging.ERROR,
        3: logging.WARNING,
        4: logging.INFO,
        5: logging.DEBUG
    }.get(val, 4)

#TODO repair
def setup_logger(level=logging.INFO, filename=None):
    log_format = ('%(asctime)s::%(levelname)s:: %(message)s')
    handlers = []
    if filename is None:
        handlers.append(setup_logger_stream())
    else:
        handlers.append(setup_logger_file(filename))
        handlers.append(setup_logger_stream())

    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )
    install_mp_handler() #DO NOT WORK, repair it

# sys.stdout mainly for debugging purposes
def setup_logger_stream():
    return logging.StreamHandler(sys.stdout)


def setup_logger_file(filename):
    return logging.FileHandler(filename)