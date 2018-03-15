import os.path as opath
import os
from functools import reduce
import datetime, time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import csv
#
IATA = 'STN'

path_join = lambda prefix, name: opath.join(prefix, name)
create_dir = lambda dpath: os.mkdir(dpath) if not opath.exists(dpath) else -1
DATA_HOME = reduce(path_join, [opath.expanduser('~'), 'Dropbox', 'Data', IATA])

create_dir(DATA_HOME)
dpaths = {}
for forWhat in ['Cargo', 'Passenger']:
    create_dir(opath.join(DATA_HOME, forWhat))
    for direction in ['Arrival', 'Departure']:
        dpath = reduce(path_join, [DATA_HOME, forWhat, direction])
        create_dir(dpath)
        dpaths[forWhat, direction] = dpath

INTERVAL = 3600 * 3


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


def get_htmlPage(url, isCargo=False):
    wd = webdriver.Firefox(executable_path=os.getcwd() + '/geckodriver')
    wd.get(url)
    WebDriverWait(wd, 15).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, 'table')))

    if isCargo:
        # Click switcher
        switcher = wd.find_element_by_class_name('switchery')
        while not switcher.is_selected():
            wd.execute_script("arguments[0].click();", switcher)
        WebDriverWait(wd, 15).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'table')))

    # And grab the page HTML source
    html_page = wd.page_source
    wd.quit()
    return html_page


def crawl_cargoDeparture():
    dt = datetime.datetime.today() - datetime.timedelta(days=1)
    fpath = opath.join(dpaths['Cargo', 'Departure'],
                       '%s-CD-%d%02d%02d.csv' % (IATA, dt.year, dt.month, dt.day))
    direction = 'departures'
    #
    handle_cargoFlights(fpath, direction)


def crawl_cargoArrival():
    dt = datetime.datetime.today() - datetime.timedelta(days=1)
    fpath = opath.join(dpaths['Cargo', 'Arrival'],
                       '%s-CA-%d%02d%02d.csv' % (IATA, dt.year, dt.month, dt.day))
    direction = 'arrivals'
    #
    handle_cargoFlights(fpath, direction)


def handle_cargoFlights(fpath, direction):
    url = 'http://www.changiairport.com/en/flight/%s.html?term=&schtime=&date=yesterday&time=all' % direction
    html_page = get_htmlPage(url, isCargo=True)
    soup = BeautifulSoup(html_page)
    all_entities = soup.find_all('tr')
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['Scheduled',
                      'Updated' if direction == 'arrivals' else 'Revised',
                      'From' if direction == 'arrivals' else 'To',
                      'Flight', 'Status']
        writer.writerow(new_header)
    for i, row in enumerate(all_entities):
        if i < 3:
            continue
        cols = row.find_all('td')
        if len(cols) != 5:
            continue
        scheduled = cols[0].find_all(class_='visible-md')[0].get_text()
        latest = cols[1].get_text().replace('\t', '').replace('\n', '').replace('()*', '')
        dest_flights = set(e.get_text() for e in cols[2].find_all(class_="ng-binding"))
        flights = set(e.get_text() for e in cols[3].find_all(class_='ng-binding'))
        locations = dest_flights.difference(flights)
        if len(locations) == 1:
            _from = locations.pop()
        else:
            vias = []
            for l in locations:
                if '\nvia' in l:
                    continue
                else:
                    if l.startswith('via '):
                        vias.append(l)
                    else:
                        final = l
            _from = '%s (%s)' % (final, ' '.join(vias))
        status = cols[4].find(class_='ng-binding').get_text()
        #
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            new_row = [scheduled, latest, _from, ';'.join(flights), status]
            writer.writerow(new_row)


def crawl_passengerDeparture():
    dt = datetime.datetime.today() - datetime.timedelta(days=1)
    fpath = opath.join(dpaths['Passenger', 'Departure'],
                       '%s-PA-%d%02d%02d.csv' % (IATA, dt.year, dt.month, dt.day))
    url = 'http://www.changiairport.com/en/flight/departures.html?term=&schtime=&date=yesterday&time=all'
    html_page = get_htmlPage(url)
    soup = BeautifulSoup(html_page)
    all_entities = soup.find_all('tr')
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['Scheduled', 'Revised', 'To', 'Flight', 'Terminal/Row/Door', 'Gate', 'Status']
        writer.writerow(new_header)

    for i, row in enumerate(all_entities):
        if i < 3:
            continue
        cols = row.find_all('td')
        if len(cols) != 7:
            continue
        scheduled = cols[0].find_all(class_='visible-md')[0].get_text()
        revised = cols[1].get_text().replace('\t', '').replace('\n', '').replace('()*', '')
        dest_flights = set(e.get_text() for e in cols[2].find_all(class_="ng-binding"))
        flights = set(e.get_text() for e in cols[3].find_all(class_='ng-binding'))
        locations = dest_flights.difference(flights)
        if len(locations) == 1:
            _from = locations.pop()
        else:
            assert len(locations) == 3
            for l in locations:
                if '\nvia' in l:
                    continue
                else:
                    if l.startswith('via '):
                        via = l
                    else:
                        final = l
            _from = '%s (%s)' % (final, via)
        terminal = cols[4].find(class_='ng-binding').get_text().replace('\t', '').replace('\n', '').replace('*', '')
        gate = cols[5].find(class_='ng-binding').get_text().replace('\n', '').replace('*', '')
        status = cols[6].find(class_='ng-binding').get_text()
        #
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            new_row = [scheduled, revised, _from, ';'.join(flights), terminal, gate, status]
            writer.writerow(new_row)

def crawl_passengerArrival():
    dt = datetime.datetime.today() - datetime.timedelta(days=1)
    fpath = opath.join(dpaths['Passenger', 'Arrival'],
                       '%s-PA-%d%02d%02d.csv' % (IATA, dt.year, dt.month, dt.day))
    url = 'http://www.changiairport.com/en/flight/arrivals.html?term=&schtime=&date=yesterday&time=all'
    html_page = get_htmlPage(url)
    soup = BeautifulSoup(html_page)
    all_entities = soup.find_all('tr')
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        new_header = ['Scheduled', 'Updated', 'From', 'Flight', 'Terminal', 'Belt', 'Status']
        writer.writerow(new_header)
    for i, row in enumerate(all_entities):
        if i < 3:
            continue
        cols = row.find_all('td')
        if len(cols) != 7:
            continue
        scheduled = cols[0].find_all(class_='visible-md')[0].get_text()
        updated = cols[1].get_text().replace('\t', '').replace('\n', '').replace('()*', '')
        dest_flights = set(e.get_text() for e in cols[2].find_all(class_="ng-binding"))
        flights = set(e.get_text() for e in cols[3].find_all(class_='ng-binding'))
        locations = dest_flights.difference(flights)
        if len(locations) == 1:
            _from = locations.pop()
        else:
            assert len(locations) == 3
            for l in locations:
                if '\nvia' in l:
                    continue
                else:
                    if l.startswith('via '):
                        via = l
                    else:
                        final = l
            _from = '%s (%s)' % (final, via)
        terminal = cols[4].find(class_='ng-binding').get_text()
        belt = cols[5].find(class_='ng-binding').get_text().replace('\n', '')
        status = cols[6].find(class_='ng-binding').get_text()
        #
        with open(fpath, 'a') as w_csvfile:
            writer = csv.writer(w_csvfile, lineterminator='\n')
            new_row = [scheduled, updated, _from, ';'.join(flights), terminal, belt, status]
            writer.writerow(new_row)


if __name__ == '__main__':
    run()