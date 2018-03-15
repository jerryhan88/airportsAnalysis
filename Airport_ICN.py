import os.path as opath
import os
from functools import reduce
import datetime, time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup



url = 'https://www.airport.kr/ap/en/dep/depPasSchList.do'

wd = webdriver.Chrome(executable_path=os.getcwd() + '/chromedriver')
wd.get(url)

WebDriverWait(wd, 15).until(EC.presence_of_all_elements_located((By.ID, 'div-result-list')))

excelDown_btn = wd.find_element_by_id('excelDown')
# excelDown_btn.click()
wd.execute_script("arguments[0].click();", excelDown_btn)
import time
# file existance check!!
time.sleep(2)

wd.quit()