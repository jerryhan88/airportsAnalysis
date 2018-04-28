import multiprocessing
import time
#
from __commons import DATA_COL_INTERVAL
#
from Airport_HGK import crawler_run as crawling_HGK
from Airport_ICN import crawler_run as crawling_ICN
from Airport_PUS import crawler_run as crawling_PUS
from Airport_SIN import crawler_run as crawling_SIN
from Airport_TPE import crawler_run as crawling_TPE


IATA_crawlingFunc = {
    'HGK': crawling_HGK,
    'ICN': crawling_ICN,
    'PUS': crawling_PUS,
    'SIN': crawling_SIN,
    'TPE': crawling_TPE
}


def run():
    while True:
        crawling_failed = {}
        for IATA, crawlingFunc in IATA_crawlingFunc.items():
            try:
                crawlingFunc()
            except:
                crawling_failed[IATA] = crawlingFunc
        if crawling_failed:
            for IATA, crawlingFunc in crawling_failed.items():
                detach_process(IATA, crawlingFunc)
        time.sleep(DATA_COL_INTERVAL)


def detach_process(IATA, crawlingFunc):
    print('Try crawling again: ', IATA)
    time.sleep(DATA_COL_INTERVAL / 3)
    p = multiprocessing.Process(target=crawlingFunc)
    p.start()


if __name__ == '__main__':
    print('Crawling')
    run()