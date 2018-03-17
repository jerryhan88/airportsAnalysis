import os.path as opath
import os
from functools import reduce
from datetime import datetime
from dateutil import tz
import pytz
from time import sleep
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from xlrd import open_workbook
import csv


IATA = 'ICN'
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

DOWN_WAIT_SEC = 2
tripStr = lambda _s: _s.replace('\n', '').replace('\t', '')


INTERVAL = 3600 * 0.5


def run():
    while True:
        try:
            crawl_cargoDeparture()
            crawl_cargoArrival()
            crawl_passengerDeparture()
            crawl_passengerArrival()
        except:
            pass
        time.sleep(INTERVAL)

def crawl_cargoInfo(url):
    wd = webdriver.Chrome(executable_path=os.getcwd() + '/chromedriver')
    wd.get(url)
    WebDriverWait(wd, 15).until(EC.presence_of_all_elements_located((By.ID, 'div-result-list')))
    # And grab the page HTML source
    html_page = wd.page_source
    wd.quit()
    return html_page

def crawl_cargoDeparture():
    dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz.gettz('Asia/Seoul'))
    fpath = opath.join(dpaths['Cargo', 'Departure'],
                       '%s-CA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    url = 'https://www.airport.kr/ap/en/dep/depCargoSchList.do'
    html_page = crawl_cargoInfo(url)
    soup = BeautifulSoup(html_page)
    all_entities = soup.find_all('div', {'class': 'flight-wrap'})
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['departure time (original)', 'departure time (changed)',
                      'Destination', 'Airlines', 'Flight name', 'Terminal', 'Flight Terminal', 'Status']
        writer.writerow(new_header)
    for i, row in enumerate(all_entities):
        destination, terminal, flightTerminal = [tripStr(ele.get_text()) for ele in
                                                row.find_all('div', {'class': 'td-like center'})]
        dt_changed, airline, flight_name = map(tripStr, [row.find('div', {'class': attr}).get_text()
                                                        for attr in ['time-changed',
                                                                     'flight-info-basic-flight-name font14',
                                                                     'flight-info-basic-flight-number']])
        try:
            dt_ori = row.find('div', {'class': 'time-due'}).get_text()
        except AttributeError:
            dt_ori = ''
        try:
            status = tripStr(row.find('span', {'class': 'situation-info type-start'}).get_text())
        except AttributeError:
            status = ''
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow([dt_ori, dt_changed, destination, airline, flight_name,
                             terminal, flightTerminal, status])


def crawl_cargoArrival():
    dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz.gettz('Asia/Seoul'))
    fpath = opath.join(dpaths['Cargo', 'Arrival'],
                       '%s-CA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    url = 'https://www.airport.kr/ap/en/arr/arrCargoSchList.do'
    html_page = crawl_cargoInfo(url)
    soup = BeautifulSoup(html_page)
    all_entities = soup.find_all('div', {'class': 'flight-wrap'})
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['arrival time (original)', 'arrival time (changed)',
                      'Starting point', 'Airlines', 'Flight name', 'Terminal', 'A ledge', 'Arrival Status']
        writer.writerow(new_header)
    for i, row in enumerate(all_entities):
        at_ori, airline, flight_name = map(tripStr, [row.find('div', {'class': attr}).get_text()
                                                        for attr in ['time-due',
                                                                     'flight-info-basic-flight-name font14',
                                                                     'flight-info-basic-flight-number']])
        try:
            at_changed = row.find('div', {'class': 'time-changed'}).get_text()
        except AttributeError:
            at_changed = ''
        startingPoint, terminal, ledge = [tripStr(ele.get_text()) for ele in
                                          row.find_all('div', {'class': 'td-like center'})]
        try:
            status = tripStr(row.find('span', {'class': 'situation-info type-start'}).get_text())
        except AttributeError:
            status = ''
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            writer.writerow([at_ori, at_changed, startingPoint, airline, flight_name,
                             terminal, ledge, status])


def download_passFlightInfos(direction, down_fpath):
    url = 'https://www.airport.kr/ap/en/%s/%sPasSchList.do' % (direction, direction)
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': os.getcwd()}
    chrome_options.add_experimental_option('prefs', prefs)
    wd = webdriver.Chrome(chrome_options=chrome_options, executable_path=os.getcwd() + '/chromedriver')
    wd.get(url)
    WebDriverWait(wd, 15).until(EC.presence_of_all_elements_located((By.ID, 'div-result-list')))
    excelDown_btn = wd.find_element_by_id('excelDown')
    wd.execute_script("arguments[0].click();", excelDown_btn)
    while True:
        if opath.exists(down_fpath):
            wd.quit()
            break
        sleep(DOWN_WAIT_SEC)
        

def crawl_passengerArrival():
    down_fpath = opath.join(os.getcwd(), 'Passenger_Arrival_Schedule.xls')
    direction = 'arr'
    download_passFlightInfos(direction, down_fpath)
    #
    dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz.gettz('Asia/Seoul'))
    fpath = opath.join(dpaths['Passenger', 'Arrival'],
                       '%s-PA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    book = open_workbook(down_fpath)
    sh = book.sheet_by_index(0)
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        writer.writerow([sh.cell(0, j).value for j in range(sh.ncols)])
        for i in range(1, sh.nrows):
            writer.writerow([sh.cell(i, j).value for j in range(sh.ncols)])
    os.remove(down_fpath)


def crawl_passengerDeparture():
    down_fpath = opath.join(os.getcwd(), 'Passenger_Departure_Schedule.xls')
    direction = 'dep'
    download_passFlightInfos(direction, down_fpath)
    #
    dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz.gettz('Asia/Seoul'))
    fpath = opath.join(dpaths['Passenger', 'Departure'],
                       '%s-PD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    book = open_workbook(down_fpath)
    sh = book.sheet_by_index(0)
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        writer.writerow([sh.cell(0, j).value for j in range(sh.ncols)])
        for i in range(1, sh.nrows):
            new_row = [sh.cell(i, j).value for j in range(4)]
            new_row += [sh.cell(i, 5).value.replace(',', ';')]
            new_row += [sh.cell(i, j).value for j in range(6, sh.ncols)]
            writer.writerow(new_row)
    os.remove(down_fpath)


if __name__ == '__main__':
    run()