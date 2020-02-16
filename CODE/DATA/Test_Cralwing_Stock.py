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
from CRAWLING import Investing


do_earnings = True

db = DB_Util.DB()
db.connet(host="127.0.0.1", port=3306, database="investing.com", user="root", password="ryumaria")


options = [['KR', 'KOSPI 200'], ['KR', 'KOSDAQ 150'], ['US', 'S&P 500'], ['US', 'Nasdaq 100'], ]

obj = Investing.InvestingStockInfo(db)
obj.Start()
time.sleep(15)

for idx, option in enumerate(options):
    country = option[0]
    group = option[1]

    obj.SetCountryGroupInfo(country, group)

    comp_info_list = obj.GetCompsInfo(idx)
    for idx_comp, comp_info in enumerate(comp_info_list):
        print('idx:\t' + str(idx_comp) + '\tpid\t' + comp_info['pid'] + '\turl:\t' + comp_info['earnings_url'])

        if do_earnings == True:
            earnings = obj.GetEarningsData(comp_info['earnings_url'], t_gap=0.1, loop_num=1)
            print(earnings)

        time.sleep(0.5)

        break

db.disconnect()