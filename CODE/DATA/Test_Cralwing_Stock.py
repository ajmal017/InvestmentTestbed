# _*_ coding: utf-8 _*_

from bs4 import BeautifulSoup
from selenium import webdriver
import sys
import os
import warnings
import platform
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

from COMM import DB_Util

db = DB_Util.DB()
db.connet(host="127.0.0.1", port=3306, database="investing.com", user="root", password="ryumaria")

options = webdriver.ChromeOptions()
if 0:
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    # 혹은 options.add_argument("--disable-gpu")

if platform.system() == 'Windows':
    wd = webdriver.Chrome('chromedriver', chrome_options=options)
else:
    wd = webdriver.Chrome('%s/chromedriver' % (os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))), chrome_options=options)

country = 'Korea'
if country == 'Korea':
    wd.get('https://www.investing.com/equities/south-korea')
    time.sleep(10)

    # group_type = wd.find_element_by_xpath('//*[@id="all"]')
    # group_type = wd.find_element_by_xpath('//*[@id="37427"]')  # KOSPI 200
    group_type = wd.find_element_by_xpath('//*[@id="980241"]') # KOSDAQ 150
    group_type.click()
    time.sleep(10)
else:
    wd.get('https://www.investing.com/equities/united-states')
    time.sleep(10)

    group_type = wd.find_element_by_xpath('//*[@id="166"]') # S&P 500
    # group_type = wd.find_element_by_xpath('//*[@id="20"]')  # Nasdaq 100
    group_type.click()
    time.sleep(10)


main_html = wd.page_source
main_bs = BeautifulSoup(main_html, 'html.parser')
data_list = main_bs.find('tbody')
print(len(data_list))
for data in data_list:

    pid = data['id'].split('_')[1]
    nm = data.find('a')['title']
    link = data.find('a')['href']
    print(pid + nm + link)
    continue

    last = data.find('td', {'class': 'pid-%s-last' % (pid)}).text
    high = data.find('td', {'class': 'pid-%s-high' % (pid)}).text
    low = data.find('td', {'class': 'pid-%s-low' % (pid)}).text
    pcp = data.find('td', {'class': 'pid-%s-pcp' % (pid)}).text
    turnover = data.find('td', {'class': 'pid-%s-turnover' % (pid)}).text


    wd.get('https://www.investing.com%s' % (link))
    sub_html = wd.page_source
    sub_bs = BeautifulSoup(sub_html, 'html.parser')
    tmp = sub_bs.find('tbody')


db.disconnect()