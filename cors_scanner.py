import math
import multiprocessing
import time

from src.cors_checker import CORSChecker
from src.utils import read_urls

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

def main():
    global sem_size
    path = "./top_100.txt"
    urls = read_urls(path)

    cpu_count = multiprocessing.cpu_count()
    part = math.ceil(len(urls)/cpu_count)
    sem_size = math.floor(1000/cpu_count)
    chunks = [urls[x:x+part] for x in range(0, len(urls), part)]

    multipool(chunks)

    # checker = CORSChecker2(urls, num)
    # checker.run()

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))