from __commons import *
#
IATA = 'PUS'
DATA_HOME = reduce(opath.join, [opath.expanduser('~'), 'Dropbox', 'Data', IATA])
DIR_PATHS = get_dpaths(DATA_HOME)


def run():
    while True:
        try:
            loc_dt = get_loc_dt('Asia/Seoul')
            crawl_PD(loc_dt)
            crawl_PA(loc_dt)
            time.sleep(DATA_COL_INTERVAL)
        except:
            time.sleep(DATA_COL_INTERVAL)
            run()

def crawl_PD(dt):
    fpath = opath.join(DIR_PATHS['Passenger', 'Departure'],
                       '%s-PD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    direction = 'departure'
    #
    handle_flightsInfo(fpath, direction)


def crawl_PA(dt):
    fpath = opath.join(DIR_PATHS['Passenger', 'Arrival'],
                       '%s-PA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    direction = 'arrival'
    #
    handle_flightsInfo(fpath, direction)


def handle_flightsInfo(fpath, direction):
    new_header = ['Airline', 'FlightNumber', 'ScheduledTime', 'ChangedTime', 'Departure', 'Arrival',
                  'Classification', 'BoardingGate' if direction == 'departure' else 'Exit', 'Status']
    init_csv_file(fpath, new_header)
    #
    url_postfix = '1&inoutType=OUT&cid=2016010821002807881&menuId=2195' if direction == 'departure' else '1&inoutType=IN&cid=2016010821004412692&menuId=2196'
    url = 'https://www.airport.co.kr/gimhaeeng/extra/liveSchedule/liveScheduleList/layOut.do?langType=%s' % url_postfix
    html_elements = get_html_elements_by_time(url)
    all_entities = html_elements.find_all('tr')
    for i, row in enumerate(all_entities):
        if i < 1:
            continue
        cols = row.find_all('td')
        if len(cols) != 9:
            continue
        Airline, FlightNo = [cols[i].get_text() for i in range(2)]
        ScheduledTime, ChangedTime = [trim_str(cols[i].get_text()) for i in range(2, 4)]
        Departure, Arrival, Classification, BoardingGate, Status = [trim_str(cols[i].get_text()) for i in range(4, 9)]
        #
        new_row = [Airline, FlightNo, ScheduledTime, ChangedTime, Departure, Arrival,
                   Classification, BoardingGate, Status]
        append_new_record2csv(fpath, new_row)


if __name__ == '__main__':
    print('Crawling %s' % IATA)
    run()
