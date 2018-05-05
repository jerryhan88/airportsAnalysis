import os.path as opath
from functools import reduce
import datetime
import csv
#
from __commons import get_dpaths, get_loc_dt
from __commons import get_html_elements_byTime
from __commons import get_ymd, get_xSummaryYMD_fns
from __commons import init_csv_file, append_new_record2csv, write_daySummary
#
IATA = 'HGK'
DATA_HOME = reduce(opath.join, [opath.expanduser('~'), 'Dropbox', 'Data', IATA])
DIR_PATHS = get_dpaths(DATA_HOME)

get_text = lambda row, dataName: row.find('td', {'class': '%sData' % dataName}).get_text()


def crawler_run():
    loc_dt = get_loc_dt('Asia/Hong_Kong')
    crawl_PD(loc_dt)
    crawl_PA(loc_dt)
    crawl_CD(loc_dt)
    crawl_CA(loc_dt)


def daySummary():
    daySummary_PD()
    daySummary_PA()
    daySummary_CD()
    daySummary_CA()


def crawl_PD(dt):
    fpath = opath.join(DIR_PATHS['Passenger', 'Departure'],
                       '%s-PD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    new_header = ['Time', 'Airline', 'Flight',
                  'Destination', 'Terminal', 'CheckIn', 'TransferDesk', 'Gate', 'Status']
    init_csv_file(fpath, new_header)
    #
    forWhat, direction = 'passenger', 'departures'
    all_entities = get_HGK_entities(forWhat, direction)
    for i, row in enumerate(all_entities):
        if i < 1:
            continue
        airlines, flights = get_airlinesNflights(row)
        transfer = '/'.join([o.get_text() for o in row.find('td', {'class': 'transferData'}).find_all('span')])
        scheduledTime, loc, terminal, checkIn, gate, status = [get_text(row, dn) for dn in ['time', 'dest', 'terminal', 'checkIn', 'gate', 'status']]
        #
        new_row = [scheduledTime, airlines, flights, loc, terminal, checkIn, transfer, gate, status]
        append_new_record2csv(fpath, new_row)


def crawl_PA(dt):
    fpath = opath.join(DIR_PATHS['Passenger', 'Arrival'],
                       '%s-PA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    new_header = ['Time', 'Airline', 'Flight',
                  'Origin', 'ParkingStand', 'Hall', 'Belt', 'Status']
    init_csv_file(fpath, new_header)
    #
    forWhat, direction = 'passenger', 'arrivals'
    all_entities = get_HGK_entities(forWhat, direction)
    for i, row in enumerate(all_entities):
        if i < 1:
            continue
        airlines, flights = get_airlinesNflights(row)
        scheduledTime, loc = [get_text(row, dn) for dn in ['time', 'origin']]
        ParkingStand, hall, belt, status = [get_text(row, dn) for dn in ['gate', 'hall', 'belt', 'status']]
        #
        new_row = [scheduledTime, airlines, flights, loc, ParkingStand, hall, belt, status]
        append_new_record2csv(fpath, new_row)


def crawl_CD(dt):
    fpath = opath.join(DIR_PATHS['Cargo', 'Departure'],
                       '%s-CD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    direction = 'departures'
    crawl_cargoInfo(direction, fpath)


def crawl_CA(dt):
    fpath = opath.join(DIR_PATHS['Cargo', 'Arrival'],
                       '%s-CA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    direction = 'arrivals'
    crawl_cargoInfo(direction, fpath)


def crawl_cargoInfo(direction, fpath):
    new_header = ['Time', 'Airline', 'Flight',
                  'Destination' if direction == 'departures' else 'Origin',
                  'Status']
    init_csv_file(fpath, new_header)
    #
    forWhat = 'cargo'
    all_entities = get_HGK_entities(forWhat, direction)
    for i, row in enumerate(all_entities):
        if i < 1:
            continue
        scheduledTime, status = [get_text(row, dn) for dn in ['time', 'status']]
        airline, flight = [o.get_text() for o in row.find('td', {'class': 'airlineData'}).find_all('span')]
        loc = ';'.join([o.get_text() for o in row.find('td', {'class': 'destData'}).find_all('li')])
        #
        new_row = [scheduledTime, airline, flight, loc, status]
        append_new_record2csv(fpath, new_row)


def get_HGK_entities(forWhat, direction):
    url = 'http://www.hongkongairport.com/en/flights/%s/%s.page' % (direction, forWhat)
    html_elements = get_html_elements_byTime(url)
    all_entities = html_elements.find_all('tr', {'class': 'data'})
    #
    return all_entities


def get_airlinesNflights(row):
    airlines, flights = [], []
    for aInstance in row.find('td', {'class': 'airlineData'}).find_all('li'):
        airline, flight = [o.get_text() for o in aInstance.find_all('span')]
        airlines.append(airline)
        flights.append(flight)
    #
    return ';'.join(airlines), ';'.join(flights)


def daySummary_PD():
    wd, dpath = 'PD', DIR_PATHS['Passenger', 'Departure']
    xSummaryYMD_fns = get_xSummaryYMD_fns(dpath, DIR_PATHS['Summary'])
    for ymd, fns in xSummaryYMD_fns.items():
        FlightLoc, rows = set(), []
        for fn in sorted(fns, reverse=True):
            year, month, day = get_ymd(ymd)
            with open(opath.join(dpath, fn)) as r_csvfile:
                reader = csv.DictReader(r_csvfile)
                for row in reader:
                    Flight, Destination = [row[cn] for cn in ['Flight', 'Destination']]
                    Flight = ';'.join(sorted(Flight.split(';')))
                    k = (Flight, Destination)
                    if k in FlightLoc: continue
                    FlightLoc.add(k)
                    Time, Airline, Terminal, Gate, Status = [row[cn] for cn in
                                                 ['Time', 'Airline', 'Terminal', 'Gate', 'Status']]
                    hour, minute = map(int, Time.split(':'))
                    dt = datetime.datetime(year, month, day, hour, minute)
                    dt_row = (dt, [Time, Airline, Flight, Destination,
                               '%s-%s' % (Terminal, Gate), Status])
                    rows.append(dt_row)
        #
        ymd_fpath = opath.join(DIR_PATHS['Summary'], '%s-%s-%s.csv' % (ymd, wd, IATA))
        write_daySummary(ymd_fpath, rows)


def daySummary_PA():
    wd, dpath = 'PA', DIR_PATHS['Passenger', 'Arrival']
    xSummaryYMD_fns = get_xSummaryYMD_fns(dpath, DIR_PATHS['Summary'])
    for ymd, fns in xSummaryYMD_fns.items():
        FlightLoc, rows = set(), []
        for fn in sorted(fns, reverse=True):
            year, month, day = get_ymd(ymd)
            with open(opath.join(dpath, fn)) as r_csvfile:
                reader = csv.DictReader(r_csvfile)
                for row in reader:
                    Flight, Origin = [row[cn] for cn in ['Flight', 'Origin']]
                    Flight = ';'.join(sorted(Flight.split(';')))
                    k = (Flight, Origin)
                    if k in FlightLoc: continue
                    FlightLoc.add(k)
                    Time, Airline, ParkingStand, Hall, Status = [row[cn] for cn in
                                                 ['Time', 'Airline', 'ParkingStand', 'Hall', 'Status']]
                    hour, minute = map(int, Time.split(':'))
                    dt = datetime.datetime(year, month, day, hour, minute)
                    dt_row = (dt, [Time, Airline, Flight, Origin,
                               '%s-%s' % (Hall, ParkingStand), Status])
                    rows.append(dt_row)
        #
        ymd_fpath = opath.join(DIR_PATHS['Summary'], '%s-%s-%s.csv' % (ymd, wd, IATA))
        write_daySummary(ymd_fpath, rows)


def daySummary_CD():
    wd, dpath = 'CD', DIR_PATHS['Cargo', 'Departure']
    xSummaryYMD_fns = get_xSummaryYMD_fns(dpath, DIR_PATHS['Summary'])
    for ymd, fns in xSummaryYMD_fns.items():
        FlightLoc, rows = set(), []
        for fn in sorted(fns, reverse=True):
            year, month, day = get_ymd(ymd)
            with open(opath.join(dpath, fn)) as r_csvfile:
                reader = csv.DictReader(r_csvfile)
                for row in reader:
                    Flight, Destination = [row[cn] for cn in ['Flight', 'Destination']]
                    Flight = ';'.join(sorted(Flight.split(';')))
                    k = (Flight, Destination)
                    if k in FlightLoc: continue
                    FlightLoc.add(k)
                    Time, Airline, Status = [row[cn] for cn in
                                                 ['Time', 'Airline', 'Status']]
                    hour, minute = map(int, Time.split(':'))
                    dt = datetime.datetime(year, month, day, hour, minute)
                    dt_row = (dt, [Time, Airline, Flight, Destination, Status])
                    rows.append(dt_row)
        #
        ymd_fpath = opath.join(DIR_PATHS['Summary'], '%s-%s-%s.csv' % (ymd, wd, IATA))
        write_daySummary(ymd_fpath, rows)


def daySummary_CA():
    wd, dpath = 'CA', DIR_PATHS['Cargo', 'Arrival']
    xSummaryYMD_fns = get_xSummaryYMD_fns(dpath, DIR_PATHS['Summary'])
    for ymd, fns in xSummaryYMD_fns.items():
        FlightLoc, rows = set(), []
        for fn in sorted(fns, reverse=True):
            year, month, day = get_ymd(ymd)
            with open(opath.join(dpath, fn)) as r_csvfile:
                reader = csv.DictReader(r_csvfile)
                for row in reader:
                    Flight, Origin = [row[cn] for cn in ['Flight', 'Origin']]
                    Flight = ';'.join(sorted(Flight.split(';')))
                    k = (Flight, Origin)
                    if k in FlightLoc: continue
                    FlightLoc.add(k)
                    Time, Airline, Status = [row[cn] for cn in
                                                 ['Time', 'Airline', 'Status']]
                    hour, minute = map(int, Time.split(':'))
                    dt = datetime.datetime(year, month, day, hour, minute)
                    dt_row = (dt, [Time, Airline, Flight, Origin, Status])
                    rows.append(dt_row)
        #
        ymd_fpath = opath.join(DIR_PATHS['Summary'], '%s-%s-%s.csv' % (ymd, wd, IATA))
        write_daySummary(ymd_fpath, rows)


if __name__ == '__main__':
    daySummary()