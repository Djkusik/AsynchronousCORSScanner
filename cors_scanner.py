import sys
import time

from common.utils import read_urls, normalize_url, timer
from common.argparser import parse_args
from common.logger import setup_logger
from core.cors_checker import CORSChecker

# GLOBALS
sem_size = 5000


def main():
    cmd_args = parse_args()
    setup_logger(cmd_args.log_level, cmd_args.log_filename)

    if cmd_args.is_path:
        urls = read_urls(cmd_args.value)
    else:
        urls = normalize_url(cmd_args.value.strip())

    if sys.platform == 'win32':
        global sem_size
        sem_size = 50

    run(urls, cmd_args)


@timer
def run(urls, cmd_args):
    global sem_size
    checker = CORSChecker(urls, sem_size, cmd_args.headers, cmd_args.char_mode, cmd_args.if_report, cmd_args.report_path)
    checker.run()


if __name__ == '__main__':
    main()
