import os.path as opath
import time
from functools import reduce
from datetime import timedelta
#
from __commons import get_dpaths, get_loc_dt
from __commons import init_csv_file, append_new_record2csv
from __commons import get_html_elements_byTAG
from __commons import DATA_COL_INTERVAL
#
IATA = 'SIN'
DATA_HOME = reduce(opath.join, [opath.expanduser('~'), 'Dropbox', 'Data', IATA])
DIR_PATHS = get_dpaths(DATA_HOME)


def crawler_run():
    loc_dt = get_loc_dt('Asia/Singapore')
    crawl_PD(loc_dt)
    crawl_PA(loc_dt)
    crawl_CD(loc_dt)
    crawl_CA(loc_dt)


def crawl_CD(dt):
    dt -= timedelta(days=1)
    fpath = opath.join(DIR_PATHS['Cargo', 'Departure'],
                       '%s-CD-%d%02d%02d.csv' % (IATA, dt.year, dt.month, dt.day))
    direction = 'departures'
    #
    handle_cargoFlights(fpath, direction)


def crawl_CA(dt):
    dt -= timedelta(days=1)
    fpath = opath.join(DIR_PATHS['Cargo', 'Arrival'],
                       '%s-CA-%d%02d%02d.csv' % (IATA, dt.year, dt.month, dt.day))
    direction = 'arrivals'
    #
    handle_cargoFlights(fpath, direction)


def handle_cargoFlights(fpath, direction):
    new_header = ['Scheduled',
                  'Updated' if direction == 'arrivals' else 'Revised',
                  'From' if direction == 'arrivals' else 'To',
                  'Flight', 'Status']
    init_csv_file(fpath, new_header)
    #
    url = 'http://www.changiairport.com/en/flight/%s.html?term=&schtime=&date=yesterday&time=all' % direction
    html_elements = get_html_elements_byTAG(url, 'table', isCargo=True)
    all_entities = html_elements.find_all('tr')
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
        new_row = [scheduled, latest, _from, ';'.join(flights), status]
        append_new_record2csv(fpath, new_row)


def crawl_PD(dt):
    dt -= timedelta(days=1)
    fpath = opath.join(DIR_PATHS['Passenger', 'Departure'],
                       '%s-PD-%d%02d%02d.csv' % (IATA, dt.year, dt.month, dt.day))
    new_header = ['Scheduled', 'Revised', 'To', 'Flight', 'Terminal/Row/Door', 'Gate', 'Status']
    init_csv_file(fpath, new_header)
    #
    url = 'http://www.changiairport.com/en/flight/departures.html?term=&schtime=&date=yesterday&time=all'
    html_elements = get_html_elements_byTAG(url, 'table')
    all_entities = html_elements.find_all('tr')
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
        new_row = [scheduled, revised, _from, ';'.join(flights), terminal, gate, status]
        append_new_record2csv(fpath, new_row)


def crawl_PA(dt):
    dt -= timedelta(days=1)
    fpath = opath.join(DIR_PATHS['Passenger', 'Arrival'],
                       '%s-PA-%d%02d%02d.csv' % (IATA, dt.year, dt.month, dt.day))
    new_header = ['Scheduled', 'Updated', 'From', 'Flight', 'Terminal', 'Belt', 'Status']
    init_csv_file(fpath, new_header)
    #
    url = 'http://www.changiairport.com/en/flight/arrivals.html?term=&schtime=&date=yesterday&time=all'
    html_elements = get_html_elements_byTAG(url, 'table')
    all_entities = html_elements.find_all('tr')
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
        new_row = [scheduled, updated, _from, ';'.join(flights), terminal, belt, status]
        append_new_record2csv(fpath, new_row)


if __name__ == '__main__':
    crawler_run()