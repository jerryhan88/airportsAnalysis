import os.path as opath
import os
from datetime import datetime, timedelta
from dateutil import tz
import pytz
import time
from functools import reduce
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from xlrd import open_workbook
import csv


DATA_COL_INTERVAL = 3600 * 0.5
PAGE_LOADING_WAITING_TIME = 10
TIME_OUT = 15


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


def init_csv_file(fpath, header):
    with open(fpath, 'wt') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        writer.writerow(header)


def append_new_record2csv(fpath, row):
    with open(fpath, 'a') as w_csvfile:
        writer = csv.writer(w_csvfile, lineterminator='\n')
        writer.writerow(row)