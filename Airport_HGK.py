import os.path as opath
import os
from functools import reduce
from datetime import datetime
from dateutil import tz
import pytz
from time import sleep
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import csv


IATA = 'HGK'
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
            dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz.gettz('Asia/Hong_Kong'))
            crawl_cargoDeparture(dt)
            crawl_cargoArrival(dt)
            crawl_passengerDeparture(dt)
            crawl_passengerArrival(dt)
            time.sleep(INTERVAL)
        except:
            time.sleep(INTERVAL)
            run()


def crawl_cargoInfo(direction, fpath):
    url = 'http://www.hongkongairport.com/en/flights/%s/cargo.page' % direction
    #
    wd = webdriver.Chrome(executable_path=os.getcwd() + '/chromedriver')
    wd.get(url)
    time.sleep(WAITING_TIME)
    # And grab the page HTML source
    html_page = wd.page_source
    wd.quit()
    #
    soup = BeautifulSoup(html_page, "html.parser")
    all_entities = soup.find_all('tr', {'class': 'data'})
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['Time', 'Airline', 'Flight',
                      'Destination' if direction == 'departures' else 'Origin',
                      'Status']
        writer.writerow(new_header)
    for i, row in enumerate(all_entities):
        if i < 1:
            continue
        scheduledTime = row.find('td', {'class': 'timeData'}).get_text()
        airline, flight = [o.get_text() for o in row.find('td', {'class': 'airlineData'}).find_all('span')]
        loc = ';'.join([o.get_text() for o in row.find('td', {'class': 'destData'}).find_all('li')])
        status = row.find('td', {'class': 'statusData'}).get_text()
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow([scheduledTime, airline, flight, loc, status])


def crawl_cargoDeparture(dt):
    fpath = opath.join(dpaths['Cargo', 'Departure'],
                       '%s-CD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    direction = 'departures'
    crawl_cargoInfo(direction, fpath)


def crawl_cargoArrival(dt):
    fpath = opath.join(dpaths['Cargo', 'Arrival'],
                       '%s-CA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    direction = 'arrivals'
    crawl_cargoInfo(direction, fpath)


def crawl_passengerInfo(direction):
    url = 'http://www.hongkongairport.com/en/flights/%s/passenger.page' % direction
    #
    wd = webdriver.Chrome(executable_path=os.getcwd() + '/chromedriver')
    wd.get(url)
    time.sleep(WAITING_TIME)
    # And grab the page HTML source
    html_page = wd.page_source
    wd.quit()
    return html_page


def crawl_passengerDeparture(dt):
    fpath = opath.join(dpaths['Passenger', 'Departure'],
                       '%s-PD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    direction = 'departures'
    html_page = crawl_passengerInfo(direction)

    soup = BeautifulSoup(html_page, "html.parser")
    all_entities = soup.find_all('tr', {'class': 'data'})
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['Time', 'Airline', 'Flight',
                      'Destination', 'Terminal', 'CheckIn', 'TransferDesk'
                      'Gate', 'Status']
        writer.writerow(new_header)
    for i, row in enumerate(all_entities):
        if i < 1:
            continue
        scheduledTime = row.find('td', {'class': 'timeData'}).get_text()
        airlines, flights = [], []
        for aInstance in row.find('td', {'class': 'airlineData'}).find_all('li'):
            airline, flight = [o.get_text() for o in aInstance.find_all('span')]
            airlines.append(airline)
            flights.append(flight)
        airlines = ';'.join(airlines)
        flights = ';'.join(flights)
        loc = row.find('td', {'class': 'destData'}).get_text()
        terminal = row.find('td', {'class': 'terminalData'}).get_text()
        checkIn = row.find('td', {'class': 'checkInData'}).get_text()
        transfer = '/'.join([o.get_text() for o in row.find('td', {'class': 'transferData'}).find_all('span')])
        gate = row.find('td', {'class': 'gateData'}).get_text()
        status = row.find('td', {'class': 'statusData'}).get_text()
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow([scheduledTime, airlines, flights, loc, terminal, checkIn, transfer, gate, status])


def crawl_passengerArrival(dt):
    fpath = opath.join(dpaths['Passenger', 'Arrival'],
                       '%s-PA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    direction = 'arrivals'
    html_page = crawl_passengerInfo(direction)
    soup = BeautifulSoup(html_page, "html.parser")
    all_entities = soup.find_all('tr', {'class': 'data'})
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['Time', 'Airline', 'Flight',
                      'Origin', 'ParkingStand', 'Hall', 'Belt', 'Status']
        writer.writerow(new_header)

    for i, row in enumerate(all_entities):
        if i < 1:
            continue
        airlines, flights = [], []
        for aInstance in row.find('td', {'class': 'airlineData'}).find_all('li'):
            airline, flight = [o.get_text() for o in aInstance.find_all('span')]
            airlines.append(airline)
            flights.append(flight)
        airlines = ';'.join(airlines)
        flights = ';'.join(flights)
        scheduledTime, loc, ParkingStand, hall, belt, status = [row.find('td', {'class': '%sData' % dn}).get_text() for dn in ['time', 'origin', 'gate', 'hall', 'belt', 'status']]
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow([scheduledTime, airlines, flights, loc, ParkingStand, hall, belt, status])


if __name__ == '__main__':
    print('Crawling %s' % IATA)
    run()