from core.cors_checker import CORSChecker
from common.utils import normalize_url, timer
from common.logger import setup_logger, log_level
import os


@timer
def web_run(url, log_lvl, log_filename, char_mode, report_path):
    setup_logger(log_level(log_lvl), log_filename)
    url = normalize_url(url.strip())
    sem_size = 5000

    checker = CORSChecker(url, sem_size, char_mode=char_mode, if_report=True, report_path=report_path)
    checker.run()
