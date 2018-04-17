from __commons import *
#
IATA = 'ICN'
DATA_HOME = reduce(opath.join, [opath.expanduser('~'), 'Dropbox', 'Data', IATA])
DIR_PATHS = get_dpaths(DATA_HOME)
#
DOWN_WAIT_SEC = 2


get_text = lambda row, attr: row.find('div', {'class': attr}).get_text()


def run():
    while True:
        try:
            loc_dt = get_loc_dt('Asia/Seoul')
            crawl_PD(loc_dt)
            crawl_PA(loc_dt)
            crawl_CD(loc_dt)
            crawl_CA(loc_dt)
            time.sleep(DATA_COL_INTERVAL)
        except:
            time.sleep(DATA_COL_INTERVAL)
            run()


def crawl_PA(dt):
    down_fpath = opath.join(os.getcwd(), 'Passenger_Arrival_Schedule.xls')
    direction = 'arr'
    download_passFlightInfos(direction, down_fpath)
    #
    fpath = opath.join(DIR_PATHS['Passenger', 'Arrival'],
                       '%s-PA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    handle_xls(down_fpath, fpath)


def crawl_PD(dt):
    down_fpath = opath.join(os.getcwd(), 'Passenger_Departure_Schedule.xls')
    direction = 'dep'
    download_passFlightInfos(direction, down_fpath)
    #
    fpath = opath.join(DIR_PATHS['Passenger', 'Departure'],
                       '%s-PD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
    handle_xls(down_fpath, fpath)


def crawl_CD(dt):
    fpath = opath.join(DIR_PATHS['Cargo', 'Departure'],
                       '%s-CD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))

    new_header = ['departure time (original)', 'departure time (changed)',
                  'Destination', 'Airlines', 'Flight name', 'Terminal', 'Flight Terminal', 'Status']
    init_csv_file(fpath, new_header)
    #
    url = 'https://www.airport.kr/ap/en/dep/depCargoSchList.do'
    html_elements = get_html_elements_by_condition(url, (By.ID, 'div-result-list'))
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
    init_csv_file(fpath, new_header)
    #
    url = 'https://www.airport.kr/ap/en/arr/arrCargoSchList.do'
    html_elements = get_html_elements_by_condition(url, (By.ID, 'div-result-list'))
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


def download_passFlightInfos(direction, down_fpath):
    url = 'https://www.airport.kr/ap/en/%s/%sPasSchList.do' % (direction, direction)
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': os.getcwd()}
    chrome_options.add_experimental_option('prefs', prefs)
    wd = webdriver.Chrome(chrome_options=chrome_options, executable_path=os.getcwd() + '/chromedriver')
    wd.get(url)
    WebDriverWait(wd, TIME_OUT).until(EC.presence_of_all_elements_located((By.ID, 'div-result-list')))
    excelDown_btn = wd.find_element_by_id('excelDown')
    wd.execute_script("arguments[0].click();", excelDown_btn)
    while True:
        if opath.exists(down_fpath):
            wd.quit()
            break
        time.sleep(DOWN_WAIT_SEC)


def handle_xls(ifpath, ofpath):
    book = open_workbook(ifpath)
    sh = book.sheet_by_index(0)
    with open(ofpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        writer.writerow([sh.cell(0, j).value for j in range(sh.ncols)])
        for i in range(1, sh.nrows):
            writer.writerow([sh.cell(i, j).value for j in range(sh.ncols)])
    os.remove(ifpath)


if __name__ == '__main__':
    print('Crawling %s' % IATA)
    run()