import functools
import linecache
import time
import logging


def normalize_url(i):
    if '://' in i:
        return [i]
    else:
        return ["http://" + i, "https://" + i]

def read_file(input_file):
    lines = linecache.getlines(input_file)
    return lines


def read_urls(path):
    urls = []
    lines = read_file(path)
    for i in lines:
        for u in normalize_url(i.strip()):
            urls.append(u)

    return urls


def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logging.info(f"--- {run_time} seconds ---")
    return wrapper_timer
