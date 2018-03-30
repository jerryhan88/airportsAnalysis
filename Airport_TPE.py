import os.path as opath
import os
from functools import reduce
from datetime import datetime, timedelta
from dateutil import tz
import pytz
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import csv
#
IATA = 'TPE'
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

INTERVAL = 3600 * 1
WAITING_TIME = 10


def run():
    while True:
        try:
            crawl_cargoDeparture()
            crawl_cargoArrival()
            crawl_passengerDeparture()
            crawl_passengerArrival()
            time.sleep(INTERVAL)
        except:
            time.sleep(INTERVAL)
            run()


def crawl_cargoDeparture():
    dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz.gettz('Asia/Taipei'))
    fpath = opath.join(dpaths['Cargo', 'Departure'],
                       '%s-CD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    purpose, direction = 'cargo', 'depart'
    #
    handle_flightsInfo(fpath, purpose, direction)


def crawl_cargoArrival():
    dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz.gettz('Asia/Taipei'))
    fpath = opath.join(dpaths['Cargo', 'Arrival'],
                       '%s-CA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    purpose, direction = 'cargo', 'arrival'
    #
    handle_flightsInfo(fpath, purpose, direction)


def crawl_passengerDeparture():
    dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz.gettz('Asia/Taipei'))
    fpath = opath.join(dpaths['Passenger', 'Departure'],
                       '%s-PD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    purpose, direction = 'flight', 'depart'
    #
    handle_flightsInfo(fpath, purpose, direction)


def crawl_passengerArrival():
    dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz.gettz('Asia/Taipei'))
    fpath = opath.join(dpaths['Passenger', 'Arrival'],
                       '%s-PA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    purpose, direction = 'flight', 'arrival'
    #
    handle_flightsInfo(fpath, purpose, direction)


def get_htmlPage(url):
    wd = webdriver.Firefox(executable_path=os.getcwd() + '/geckodriver')
    wd.get(url)
    time.sleep(WAITING_TIME)
    html_page = wd.page_source
    wd.quit()
    return html_page


def handle_flightsInfo(fpath, purpose, direction):
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['ScheduledTime', 'Airline', 'FlightNo.',
                      'Destination(Via)' if direction == 'depart' else 'Origin(Via)',
                      'Terminal',
                      'Gate/Check-inCounter' if direction == 'depart' else 'Gate/BaggageCarousel',
                      'PlaneType', 'Status']
        writer.writerow(new_header)
    url = 'https://www.taoyuan-airport.com/english/%s_%s' % (purpose, direction)
    html_page = get_htmlPage(url)
    soup = BeautifulSoup(html_page)
    all_entities = soup.find_all('tr')
    for i, row in enumerate(all_entities):
        if i < 7:
            continue
        cols = row.find_all('td')
        if len(cols) != 10:
            continue
        ScheduledTime = cols[0].get_text()
        Airline = cols[1].get_text().replace('\n', '').strip()
        FlightNo = cols[2].get_text().replace('\n', '').strip()
        if '  ' in Airline:
            Airline = ';'.join([s for s in Airline.split('  ') if s])
            FlightNo = ';'.join([s for s in FlightNo.split('  ') if s])
        loc = cols[4].get_text().replace('\n', '').strip()
        Terminal = cols[5].get_text()
        Gate = cols[6].get_text().replace('\n', '').replace('\t', '').replace(' ', '').strip()
        PlaneType = cols[7].get_text().replace('\n', '').strip()
        Status = cols[8].get_text()
        #
        if FlightNo == 'XX-0000':
            continue
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            new_row = [ScheduledTime, Airline, FlightNo, loc,
                        Terminal, Gate, PlaneType, Status]
            writer.writerow(new_row)


if __name__ == '__main__':
    print('Crawling %s' % IATA)
    run()
