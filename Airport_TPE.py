import os.path as opath
import time
from functools import reduce
#
from __commons import get_dpaths, get_loc_dt
from __commons import get_html_elements_byTime
from __commons import init_csv_file, append_new_record2csv
from __commons import trim_str
from __commons import DATA_COL_INTERVAL
#
IATA = 'TPE'
DATA_HOME = reduce(opath.join, [opath.expanduser('~'), 'Dropbox', 'Data', IATA])
DIR_PATHS = get_dpaths(DATA_HOME)


def crawler_run():
    loc_dt = get_loc_dt('Asia/Taipei')
    crawl_PD(loc_dt)
    crawl_PA(loc_dt)
    crawl_CD(loc_dt)
    crawl_CA(loc_dt)


def run():
    while True:
        try:
            loc_dt = get_loc_dt('Asia/Taipei')
            crawl_PD(loc_dt)
            crawl_PA(loc_dt)
            crawl_CD(loc_dt)
            crawl_CA(loc_dt)
            time.sleep(DATA_COL_INTERVAL)
        except:
            time.sleep(DATA_COL_INTERVAL)
            run()


def crawl_PD(dt):
    fpath = opath.join(DIR_PATHS['Passenger', 'Departure'],
                       '%s-PD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    purpose, direction = 'flight', 'depart'
    #
    handle_flightsInfo(fpath, purpose, direction)


def crawl_PA(dt):
    fpath = opath.join(DIR_PATHS['Passenger', 'Arrival'],
                       '%s-PA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    purpose, direction = 'flight', 'arrival'
    #
    handle_flightsInfo(fpath, purpose, direction)


def crawl_CD(dt):
    fpath = opath.join(DIR_PATHS['Cargo', 'Departure'],
                       '%s-CD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    purpose, direction = 'cargo', 'depart'
    #
    handle_flightsInfo(fpath, purpose, direction)


def crawl_CA(dt):
    fpath = opath.join(DIR_PATHS['Cargo', 'Arrival'],
                       '%s-CA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    purpose, direction = 'cargo', 'arrival'
    #
    handle_flightsInfo(fpath, purpose, direction)


def handle_flightsInfo(fpath, purpose, direction):
    new_header = ['ScheduledTime', 'Airline', 'FlightNo.',
                  'Destination(Via)' if direction == 'depart' else 'Origin(Via)',
                  'Terminal',
                  'Gate/Check-inCounter' if direction == 'depart' else 'Gate/BaggageCarousel',
                  'PlaneType', 'Status']
    init_csv_file(fpath, new_header)
    #
    url = 'https://www.taoyuan-airport.com/english/%s_%s' % (purpose, direction)
    html_elements = get_html_elements_byTime(url)
    all_entities = html_elements.find_all('tr')
    for i, row in enumerate(all_entities):
        if i < 7:
            continue
        cols = row.find_all('td')
        if len(cols) != 10:
            continue
        ScheduledTime, Airline, FlightNo = [trim_str(cols[i].get_text()) for i in range(3)]
        if FlightNo == 'XX-0000':
            continue
        if '  ' in Airline:
            Airline = ';'.join([s for s in Airline.split('  ') if s])
            FlightNo = ';'.join([s for s in FlightNo.split('  ') if s])
        loc, Terminal, Gate, PlaneType, Status = [trim_str(cols[i].get_text()) for i in range(4, 9)]
        #
        new_row = [ScheduledTime, Airline, FlightNo, loc,
                   Terminal, Gate, PlaneType, Status]
        append_new_record2csv(fpath, new_row)


if __name__ == '__main__':
    print('Crawling %s' % IATA)
    run()
