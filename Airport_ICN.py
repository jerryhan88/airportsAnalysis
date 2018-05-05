import os.path as opath
from functools import reduce
import datetime
import csv
#
from __commons import get_dpaths, get_loc_dt
from __commons import get_html_elements_byID
from __commons import get_ymd, get_xSummaryYMD_fns
from __commons import init_csv_file, append_new_record2csv, write_daySummary
from __commons import trim_str
#
IATA = 'ICN0'
DATA_HOME = reduce(opath.join, [opath.expanduser('~'), 'Dropbox', 'Data', IATA])
DIR_PATHS = get_dpaths(DATA_HOME)
#


def get_text(row, attr):
    if row.find('div', {'class': attr}):
        return row.find('div', {'class': attr}).get_text()
    else:
        return ''


def crawler_run():
    loc_dt = get_loc_dt('Asia/Seoul')
    crawl_PD(loc_dt)
    crawl_PA(loc_dt)
    crawl_CD(loc_dt)
    crawl_CA(loc_dt)


def daySummary():
    daySummary_PD()
    # daySummary_PA()
    # daySummary_CD()
    # daySummary_CA()


def crawl_PD(dt):
    fpath = opath.join(DIR_PATHS['Passenger', 'Departure'],
                       '%s-PD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    new_header = ['departure time (original)', 'departure time (changed)',
                  'Destination', 'Airlines', 'Flight name',
                  'Terminal', 'Check-in Counter', 'Gate', 'Status']
    if not opath.exists(fpath):
        init_csv_file(fpath, new_header)
    url = 'https://www.airport.kr/ap/en/dep/depPasSchList.do'
    html_elements = get_html_elements_byID(url, 'div-result-list')
    all_entities = html_elements.find_all('div', {'class': 'flight-info-basic-link'})
    for i, row in enumerate(all_entities):
        destination, terminal, checkInCounter, gate = [trim_str(ele.get_text()) for ele in
                                                 row.find_all('div', {'class': 'td-like center'})]
        dt_changed, airline, flight_name = map(trim_str, [get_text(row, attr)
                                                          for attr in ['time-changed',
                                                                     'flight-info-basic-flight-name font14',
                                                                     'flight-info-basic-flight-number']])
        try:
            dt_ori = get_text(row, 'time-due')
        except AttributeError:
            dt_ori = ''
        try:
            status = trim_str(row.find('span', {'class': 'situation-info type-start'}).get_text())
        except AttributeError:
            status = ''
        new_row = [dt_ori, dt_changed, destination, airline, flight_name, 
                    terminal, checkInCounter, gate, status]
        append_new_record2csv(fpath, new_row)


def crawl_PA(dt):
    fpath = opath.join(DIR_PATHS['Passenger', 'Arrival'],
                       '%s-PA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))

    new_header = ['arrival time (original)', 'arrival time (changed)',
                  'Starting point', 'Airlines', 'Flight name', 
                  'Terminal', 'Arrival gate', 'Baggage claim', 'Exit', 'Arrival Status']
    if not opath.exists(fpath):
        init_csv_file(fpath, new_header)
    #
    url = 'https://www.airport.kr/ap/en/arr/arrPasSchList.do'
    html_elements = get_html_elements_byID(url, 'div-result-list')
    all_entities = html_elements.find_all('div', {'class': 'flight-info-basic-link'})
    for i, row in enumerate(all_entities):
        startingPoint, terminal, arrivalGate, baggageClaim, exit_ = [trim_str(ele.get_text()) for ele in
                                          row.find_all('div', {'class': 'td-like center'})]
        at_ori, airline, flight_name = map(trim_str, [get_text(row, attr)
                                                      for attr in ['time-due',
                                                                     'flight-info-basic-flight-name font14',
                                                                     'flight-info-basic-flight-number']])
        try:
            at_changed = row.find('div', {'class': 'time-changed'}).get_text()
        except AttributeError:
            at_changed = ''
        try:
            status = trim_str(row.find('span', {'class': 'situation-info type-start'}).get_text())
        except AttributeError:
            status = ''
        new_row = [at_ori, at_changed, startingPoint, airline, flight_name, 
                    terminal, arrivalGate, baggageClaim, exit_, status]
        append_new_record2csv(fpath, new_row)
        

def crawl_CD(dt):
    fpath = opath.join(DIR_PATHS['Cargo', 'Departure'],
                       '%s-CD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))

    new_header = ['departure time (original)', 'departure time (changed)',
                  'Destination', 'Airlines', 'Flight name', 'Terminal', 'Flight Terminal', 'Status']
    if not opath.exists(fpath):
        init_csv_file(fpath, new_header)
    #
    url = 'https://www.airport.kr/ap/en/dep/depCargoSchList.do'
    html_elements = get_html_elements_byID(url, 'div-result-list')
    all_entities = html_elements.find_all('div', {'class': 'flight-wrap'})
    for i, row in enumerate(all_entities):
        destination, terminal, flightTerminal = [trim_str(ele.get_text()) for ele in
                                                 row.find_all('div', {'class': 'td-like center'})]
        dt_changed, airline, flight_name = map(trim_str, [get_text(row, attr)
                                                          for attr in ['time-changed',
                                                                     'flight-info-basic-flight-name font14',
                                                                     'flight-info-basic-flight-number']])
        try:
            dt_ori = get_text(row, 'time-due')
        except AttributeError:
            dt_ori = ''
        try:
            status = trim_str(row.find('span', {'class': 'situation-info type-start'}).get_text())
        except AttributeError:
            status = ''
        new_row = [dt_ori, dt_changed, destination, airline, flight_name, terminal, flightTerminal, status]
        append_new_record2csv(fpath, new_row)


def crawl_CA(dt):
    fpath = opath.join(DIR_PATHS['Cargo', 'Arrival'],
                       '%s-CA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    new_header = ['arrival time (original)', 'arrival time (changed)',
                  'Starting point', 'Airlines', 'Flight name', 'Terminal', 'A ledge', 'Arrival Status']
    if not opath.exists(fpath):
        init_csv_file(fpath, new_header)
    #
    url = 'https://www.airport.kr/ap/en/arr/arrCargoSchList.do'
    html_elements = get_html_elements_byID(url, 'div-result-list')
    all_entities = html_elements.find_all('div', {'class': 'flight-wrap'})
    for i, row in enumerate(all_entities):
        startingPoint, terminal, ledge = [trim_str(ele.get_text()) for ele in
                                          row.find_all('div', {'class': 'td-like center'})]
        at_ori, airline, flight_name = map(trim_str, [get_text(row, attr)
                                                      for attr in ['time-due',
                                                                     'flight-info-basic-flight-name font14',
                                                                     'flight-info-basic-flight-number']])
        try:
            at_changed = row.find('div', {'class': 'time-changed'}).get_text()
        except AttributeError:
            at_changed = ''
        try:
            status = trim_str(row.find('span', {'class': 'situation-info type-start'}).get_text())
        except AttributeError:
            status = ''
        new_row = [at_ori, at_changed, startingPoint, airline, flight_name, terminal, ledge, status]
        append_new_record2csv(fpath, new_row)

# S_PD_HEADER = ['Time', 'Airline', 'Flight', 'Destination', 'TG', 'Status']
def daySummary_PD():
    wd, dpath = 'PD', DIR_PATHS['Passenger', 'Departure']
    xSummaryYMD_fns = get_xSummaryYMD_fns(dpath, DIR_PATHS['Summary'])
    for ymd, fns in xSummaryYMD_fns.items():
        FlightLoc, rows = set(), []
        for fn in sorted(fns, reverse=True):
            year, month, day = get_ymd(ymd)
            with open(opath.join(dpath, fn)) as r_csvfile:
                reader = csv.DictReader(r_csvfile)
                for row1 in reader:
                    Flight, Destination = [row1[cn] for cn in ['Flight name', 'Destination']]
                    Flight = ';'.join(sorted(Flight.split(';')))
                    k = (Flight, Destination)
                    if k in FlightLoc:
                        continue
                    FlightLoc.add(k)
                    Time, Airline, Terminal, Gate, Status = [row1[cn] for cn in
                                                 ['departure time (changed)', 'Airlines', 'Terminal', 'Gate', 'Status']]
                    hour, minute = map(int, Time.split(':'))
                    dt = datetime.datetime(year, month, day, hour, minute)
                    dt_row = (dt, [Time, Airline, Flight, Destination,
                               '%s-%s' % (Terminal, Gate), Status])
                    rows.append(dt_row)
        #
        new_rows = []
        dt0, loc0, row0 = None, None, None
        saving_Airlines, saving_Flights = [], []
        for dt1, row1 in sorted(rows):
            Airline, Flight, loc1 = [row1[i] for i in range(1, 4)]
            if dt0 is None:
                dt0, loc0, row0 = dt1, loc1, row1
                saving_Airlines.append(Airline)
                saving_Flights.append(Flight)
                continue
            if dt1 == dt0 and loc1 == loc0:
                saving_Airlines.append(Airline)
                saving_Flights.append(Flight)
                continue
            else:
                dt_row = (dt0, [row0[0], ';'.join(saving_Airlines), ';'.join(saving_Flights),
                                row0[3], row0[4], row0[5]])
                new_rows.append(dt_row)
                #
                saving_Airlines, saving_Flights = [], []
                dt0, loc0, row0 = dt1, loc1, row1
                saving_Airlines.append(Airline)
                saving_Flights.append(Flight)
        dt_row = (dt0, [row0[0], ';'.join(saving_Airlines), ';'.join(saving_Flights),
                        row0[3], row0[4], row0[5]])
        new_rows.append(dt_row)
        #
        ymd_fpath = opath.join(DIR_PATHS['Summary'], '%s-%s-%s.csv' % (ymd, wd, IATA))
        write_daySummary(ymd_fpath, new_rows)


if __name__ == '__main__':
    crawler_run()