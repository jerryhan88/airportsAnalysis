from __commons import *
#
IATA = 'HGK'
DATA_HOME = reduce(opath.join, [opath.expanduser('~'), 'Dropbox', 'Data', IATA])
DIR_PATHS = get_dpaths(DATA_HOME)

get_text = lambda row, dataName: row.find('td', {'class': '%sData' % dataName}).get_text()

def run():
    while True:
        try:
            loc_dt = get_loc_dt('Asia/Hong_Kong')
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
    html_elements = get_html_elements_by_time(url)
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





if __name__ == '__main__':
    print('Crawling %s' % IATA)
    run()