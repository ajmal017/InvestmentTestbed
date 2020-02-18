# _*_ coding: utf-8 _*_

from bs4 import BeautifulSoup
from selenium import webdriver
import sys
import os
import warnings
import platform
import time
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

from COMM import DB_Util
from CRAWLING import Investing


do_profile = True
do_financial = False
do_earnings = False

db = DB_Util.DB()
db.connet(host="127.0.0.1", port=3306, database="investing.com", user="root", password="ryumaria")


options = [['KR', 'KOSPI 200'], ['KR', 'KOSDAQ 150'], ['US', 'S&P 500'], ['US', 'Nasdaq 100'], ]

obj = Investing.InvestingStockInfo(db)
obj.Start()
#time.sleep(15)

stocks_list = []
for idx, option in enumerate(options):

    country = option[0]
    group = option[1]

    obj.SetCountryGroupInfo(country, group)



    # 주식의 기본 정보를 새로 크롤링 함.
    if do_profile == True:

        columns = ['pid', 'country', 'nm', 'industry', 'sector', 'url', 'profile_url', 'financial_url', 'earnings_url']
        comp_info_list = obj.GetCompsInfo(columns, idx)

        for idx_comp, comp_info in comp_info_list.iterrows():

            '''
            # 요청이 너무 많은 경우 원격 호스트에 의해 강제로 끊는담.
            # 처리된 종목까지는 패스
            if option[1] == 'S&P 500' and idx_comp < 312:
                continue
            '''

            # 동일 종목이 여러 지수에 중복 편입되어 있는 경우 패스
            if comp_info['pid'] in stocks_list:
                print(comp_info['nm'] + '는 이미 등록되어 있음.')
                continue
            else:
                stocks_list.append(comp_info['pid'])

            comp_info = obj.GetProfileData(comp_info['profile_url'], comp_info)
            #print(profile)


            sql = "INSERT INTO stock_master (pid, country, nm, industry, sector, url, profile_url, financial_url, earnings_url)" \
                  "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" \
                  "ON DUPLICATE KEY UPDATE country='%s', nm='%s', industry='%s', sector='%s', url='%s', profile_url='%s', financial_url='%s', earnings_url='%s'"
            sql_arg = (comp_info['pid'], option[0], comp_info['nm'], comp_info['industry'], comp_info['sector'], comp_info['url'], comp_info['profile_url'], comp_info['financial_url'], comp_info['earnings_url']
                       , option[0], comp_info['nm'], comp_info['industry'], comp_info['sector'], comp_info['url'], comp_info['profile_url'], comp_info['financial_url'], comp_info['earnings_url'])
            if (db.execute_query(sql, sql_arg) == False):
                print("stock_master insert error")
            else:
                print('idx:\t' + str(idx_comp) + '\tnm\t' + comp_info['nm']
                      + '\tindustry\t' + comp_info['industry'] + '\tsector\t' + comp_info['sector']
                      + '\tpid\t' + comp_info['pid'] + '\turl\t' + comp_info['url']
                      + '\tprofile_url:\t' + comp_info['profile_url']
                      + '\tfinancial_url:\t' + comp_info['financial_url']
                      + '\tearnings_url:\t' + comp_info['earnings_url'])
    else:
        sql = "SELECT pid, country, nm, industry, sector, url, profile_url, financial_url, earnings_url" \
              "  FROM stock_master"
        columns = ['pid', 'country', 'nm', 'industry', 'sector', 'url', 'profile_url', 'financial_url', 'earnings_url']
        comp_info_list = db.select_query(query=sql, columns=columns)


    if do_financial == True:
        financial = obj.GetFinancialData(comp_info['financial_url'])
        print(financial)

    if do_earnings == True:
        earnings = obj.GetEarningsData(comp_info['earnings_url'], t_gap=0.1, loop_num=1)
        print(earnings)

        time.sleep(5)

        #break

db.disconnect()