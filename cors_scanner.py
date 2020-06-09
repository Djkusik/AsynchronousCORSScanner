import math
import multiprocessing
import time

from common.utils import read_urls, normalize_url
from common.argparser import parse_args
from core.cors_checker import CORSChecker

sem_size = 250

def worker(urls):
    checker = CORSChecker(urls, sem_size)
    checker.run()


def multipool(urls):
    try:
        p = multiprocessing.Pool()
        p.map(worker, urls)
    except:
        # add exception handling
        return


def run(urls):
    global sem_size
    cpu_count = multiprocessing.cpu_count()
    part = math.ceil(len(urls) / cpu_count)
    sem_size = math.floor(1000 / cpu_count)
    chunks = [urls[x:x + part] for x in range(0, len(urls), part)]

    multipool(chunks)


def main():
    is_path, value, verbose = parse_args()
    if is_path:
        urls = read_urls(value)
    else:
        urls = normalize_url(value.strip())

    run(urls)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))