from core.cors_checker import CORSChecker
from common.statistics import Statistics
from common.utils import normalize_url, timer
from common.logger import setup_logger, log_level
import os


@timer
def web_run(url, log_lvl, log_path, char_mode, report_path, report_name):
    if not os.path.isdir(log_path):
            os.mkdir(log_path)
    if not os.path.isdir(report_path):
            os.mkdir(report_path)
    
    setup_logger(log_level(log_lvl), f"{log_path}/cors.log")
    url = normalize_url(url.strip())
    sem_size = 5000

    stats = Statistics(report_path, report_name)
    checker = CORSChecker(url, sem_size, char_mode=char_mode, stats=stats, if_report=True)
    checker.run()
