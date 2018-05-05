import os.path as opath
import os
from datetime import datetime
from dateutil import tz
import pytz
import time
from functools import reduce
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv


DATA_COL_INTERVAL = 3600 * (1 / 6)
PAGE_LOADING_WAITING_TIME = 10
TIME_OUT = 15


S_PD_HEADER = ['Time', 'Airline', 'Flight', 'Destination', 'TG', 'Status']
S_PA_HEADER = ['Time', 'Airline', 'Flight', 'Origin', 'TG', 'Status']
S_CD_HEADER = ['Time', 'Airline', 'Flight', 'Destination', 'Status']
S_CA_HEADER = ['Time', 'Airline', 'Flight', 'Origin', 'Status']


mkdir = lambda dpath: os.mkdir(dpath) if not opath.exists(dpath) else -1
get_loc_dt = lambda loc: datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz.gettz(loc))
trim_str = lambda s0: s0.replace('\n', '').replace('\t', '').replace(' ', '').strip()


def get_dpaths(data_home):
    mkdir(data_home)
    dpaths = {}
    for forWhat in ['Cargo', 'Passenger']:
        mkdir(opath.join(data_home, forWhat))
        for direction in ['Arrival', 'Departure']:
            dpath = reduce(opath.join, [data_home, forWhat, direction])
            mkdir(dpath)
            dpaths[forWhat, direction] = dpath
    dpath = reduce(opath.join, [data_home, 'Summary'])
    mkdir(dpath)
    dpaths['Summary'] = dpath
    return dpaths


def get_html_elements_byTime(url):
    wd = webdriver.Chrome(executable_path=os.getcwd() + '/chromedriver')
    wd.get(url)
    time.sleep(PAGE_LOADING_WAITING_TIME)
    html_page = wd.page_source
    wd.quit()
    #
    html_elements = BeautifulSoup(html_page, "html.parser")
    return html_elements


def get_html_elements_byID(url, idLabel):
    wd = webdriver.Chrome(executable_path=os.getcwd() + '/chromedriver')
    wd.get(url)
    WebDriverWait(wd, TIME_OUT).until(EC.presence_of_all_elements_located((By.ID, idLabel)))
    html_page = wd.page_source
    wd.quit()
    #
    html_elements = BeautifulSoup(html_page, "html.parser")
    return html_elements


def get_html_elements_byTAG(url, tagLabel, isCargo=False):
    wd = webdriver.Firefox(executable_path=os.getcwd() + '/geckodriver')
    wd.get(url)
    WebDriverWait(wd, TIME_OUT).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, tagLabel)))
    if isCargo:
        # Click switcher
        switcher = wd.find_element_by_class_name('switchery')
        while not switcher.is_selected():
            wd.execute_script("arguments[0].click();", switcher)
        WebDriverWait(wd, TIME_OUT).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, tagLabel)))
    html_page = wd.page_source
    wd.quit()
    #
    html_elements = BeautifulSoup(html_page, "html.parser")
    return html_elements


def get_xSummaryYMD_fns(raw_dpath, summary_dpath):
    xSummaryYMD_fns = {}
    for fn in sorted(os.listdir(raw_dpath)):
        if not fn.endswith('.csv'):
            continue
        IATA, wd, dayHour = fn[:-len('.csv')].split('-')
        ymd, hour = dayHour.split('H')
        ymd_fpath = opath.join(summary_dpath, '%s-%s-%s.csv' % (ymd, wd, IATA))
        if opath.exists(ymd_fpath):
            continue
        if ymd not in xSummaryYMD_fns:
            xSummaryYMD_fns[ymd] = []
        xSummaryYMD_fns[ymd].append(fn)
    return xSummaryYMD_fns


def get_ymd(_yyyymmdd):
    year, month, day = map(int, [_yyyymmdd[:len('yyyy')],
                                 _yyyymmdd[len('yyyy'):len('yyyymm')],
                                 _yyyymmdd[len('yyyymm'):]])
    return year, month, day


def init_csv_file(fpath, header):
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        writer.writerow(header)


def append_new_record2csv(fpath, row):
    with open(fpath, 'a') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        writer.writerow(row)


def write_daySummary(ymd_fpath, rows):
    fn = os.path.basename(ymd_fpath)
    _, wd, _ = fn[:-len('.csv')].split('-')
    if wd == 'PD':
        header = S_PD_HEADER
    elif wd == 'PA':
        header = S_PA_HEADER
    elif wd == 'CD':
        header = S_CD_HEADER
    else:
        assert wd == 'CA'
        header = S_CD_HEADER

    init_csv_file(ymd_fpath, header)
    for _, row in sorted(rows):
        append_new_record2csv(ymd_fpath, row)