import sys
import time
import math
import logging
import multiprocessing

from common.utils import read_urls, normalize_url
from common.argparser import parse_args
from common.logger import setup_logger
from core.cors_checker import CORSChecker

# GLOBALS
sem_size = 250


def main():
    cmd_args = parse_args()
    setup_logger(cmd_args.log_level, cmd_args.log_filename)

    if cmd_args.is_path:
        urls = read_urls(cmd_args.value)
    else:
        urls = normalize_url(cmd_args.value.strip())

    run(urls)


def run(urls):
    global sem_size
    cpu_count = multiprocessing.cpu_count()
    part_size = math.ceil(len(urls) / cpu_count)
    sem_size = math.floor(1000 / cpu_count)
    chunks = [urls[x:x + part_size] for x in range(0, len(urls), part_size)]

    run_multi_pool(chunks)


def run_multi_pool(urls):
    try:
        p = multiprocessing.Pool()
        p.map(worker, urls)
    except Exception:
        logging.critical("Something went wrong with multiprocessing pool", exc_info=True)
        sys.exit(1)


def worker(urls):
    checker = CORSChecker(urls, sem_size)
    checker.run()


if __name__ == '__main__':
    start_time = time.time()
    main()
    logging.info(f"--- {time.time() - start_time} seconds ---")