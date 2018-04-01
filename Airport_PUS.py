import os.path as opath
import os
from functools import reduce
from datetime import datetime
from dateutil import tz
import pytz
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import csv
#
IATA = 'PUS'
create_dir = lambda dpath: os.mkdir(dpath) if not opath.exists(dpath) else -1
DATA_HOME = reduce(opath.join, [opath.expanduser('~'), 'Dropbox', 'Data', IATA])

create_dir(DATA_HOME)
dpaths = {}
for forWhat in ['Cargo', 'Passenger']:
    create_dir(opath.join(DATA_HOME, forWhat))
    for direction in ['Arrival', 'Departure']:
        dpath = reduce(opath.join, [DATA_HOME, forWhat, direction])
        create_dir(dpath)
        dpaths[forWhat, direction] = dpath

INTERVAL = 3600 * 0.5
WAITING_TIME = 10


def run():
    while True:
        try:
            crawl_passengerDeparture()
            crawl_passengerArrival()
            time.sleep(INTERVAL)
        except:
            time.sleep(INTERVAL)
            run()


def get_htmlPage(url):
    wd = webdriver.Firefox(executable_path=os.getcwd() + '/geckodriver')
    wd.get(url)
    time.sleep(WAITING_TIME)
    html_page = wd.page_source
    wd.quit()
    return html_page


def handle_flightsInfo(fpath, direction):
    url_postfix = '1&inoutType=OUT&cid=2016010821002807881&menuId=2195' if direction == 'departure' else '1&inoutType=IN&cid=2016010821004412692&menuId=2196'
    url = 'https://www.airport.co.kr/gimhaeeng/extra/liveSchedule/liveScheduleList/layOut.do?langType=%s' % url_postfix
    html_page = get_htmlPage(url)
    soup = BeautifulSoup(html_page, "html.parser")
    all_entities = soup.find_all('tr')
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['Airline', 'FlightNumber', 'ScheduledTime', 'ChangedTime', 'Departure', 'Arrival',
                      'Classification', 'BoardingGate' if direction == 'departure' else 'Exit', 'Status']
        writer.writerow(new_header)
    for i, row in enumerate(all_entities):
        if i < 1:
            continue
        cols = row.find_all('td')
        if len(cols) != 9:
            continue
        Airline, FlightNo = [cols[i].get_text() for i in range(2)]
        ScheduledTime, ChangedTime = [cols[i].get_text().replace('\n', '').replace(' ', '').strip() for i in
                                      range(2, 4)]
        Departure, Arrival, Classification, BoardingGate, Status = [
            cols[i].get_text().replace('\n', '').replace(' ', '').strip() for i in range(4, 9)]
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow(
                [Airline, FlightNo, ScheduledTime, ChangedTime, Departure, Arrival, Classification, BoardingGate,
                 Status])


def crawl_passengerDeparture():
    dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz.gettz('Asia/Seoul'))
    fpath = opath.join(dpaths['Passenger', 'Departure'],
                       '%s-PD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    direction = 'departure'
    #
    handle_flightsInfo(fpath, direction)


def crawl_passengerArrival():
    dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz.gettz('Asia/Seoul'))
    fpath = opath.join(dpaths['Passenger', 'Arrival'],
                       '%s-PA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    direction = 'arrival'
    #
    handle_flightsInfo(fpath, direction)


if __name__ == '__main__':
    print('Crawling %s' % IATA)
    run()
