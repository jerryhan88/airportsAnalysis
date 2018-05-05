# DOWN_WAIT_SEC = 2


# def crawl_PA0(dt):
#     down_fpath = opath.join(os.getcwd(), 'Passenger_Arrival_Schedule.xls')
#     direction = 'arr'
#     download_passFlightInfos(direction, down_fpath)
#     #
#     fpath = opath.join(DIR_PATHS['Passenger', 'Arrival'],
#                       '%s-PA-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
#     handle_xls(down_fpath, fpath)


# def crawl_PD0(dt):
#     down_fpath = opath.join(os.getcwd(), 'Passenger_Departure_Schedule.xls')
#     direction = 'dep'
#     download_passFlightInfos(direction, down_fpath)
#     #
#     fpath = opath.join(DIR_PATHS['Passenger', 'Departure'],
#                        '%s-PD-%d%02d%02dH%02d.csv' % (IATA, dt.year, dt.month, dt.day, dt.hour))
#     handle_xls(down_fpath, fpath)


# def download_passFlightInfos(direction, down_fpath):
#     url = 'https://www.airport.kr/ap/en/%s/%sPasSchList.do' % (direction, direction)
#     chrome_options = webdriver.ChromeOptions()
#     prefs = {'download.default_directory': os.getcwd()}
#     chrome_options.add_experimental_option('prefs', prefs)
#     wd = webdriver.Chrome(chrome_options=chrome_options, executable_path=os.getcwd() + '/chromedriver')
#     wd.get(url)
#     WebDriverWait(wd, TIME_OUT).until(EC.presence_of_all_elements_located((By.ID, 'div-result-list')))
#     excelDown_btn = wd.find_element_by_id('excelDown')
#     wd.execute_script("arguments[0].click();", excelDown_btn)
#     while True:
#         if opath.exists(down_fpath):
#             wd.quit()
#             break
#         time.sleep(DOWN_WAIT_SEC)


# def handle_xls(ifpath, ofpath):
#     book = open_workbook(ifpath)
#     sh = book.sheet_by_index(0)
#     with open(ofpath, 'wt') as w_csvfile:
#         writer = csv.writer(w_csvfile, lineterminator='\n')
#         writer.writerow([sh.cell(0, j).value for j in range(sh.ncols)])
#         for i in range(1, sh.nrows):
#             writer.writerow([sh.cell(i, j).value for j in range(sh.ncols)])
#     os.remove(ifpath)
