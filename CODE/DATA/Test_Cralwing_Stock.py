# _*_ coding: utf-8 _*_

from bs4 import BeautifulSoup
from selenium import webdriver
import sys
import os
import warnings
import platform
import time
import pandas as pd
import numpy as np
from datetime import date
from datetime import datetime
from datetime import timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

from COMM import DB_Util
from CRAWLING import Investing

loop_sleep_term = 1
do_profile = False
do_financial = False
do_earnings = False
do_dividends = False
do_price = True

db = DB_Util.DB()
db.connet(host="127.0.0.1", port=3306, database="investing.com", user="root", password="ryumaria")


options = [['KR', 'KOSPI 200'], ['KR', 'KOSDAQ 150'], ['US', 'S&P 500'], ['US', 'Nasdaq 100'], ]

obj = Investing.InvestingStockInfo(db)
obj.Start()
#time.sleep(15)

# 주식의 기본 정보 크롤링
if do_profile == True:

    stocks_list = []
    for idx, option in enumerate(options):
        country = option[0]
        group = option[1]

        # 종목리스트 생성을 위한 국가별 대표지수 설정
        obj.SetCountryGroupInfo(country, group)

        # 대표지수에 포함되어 있는 종목 리스트 및 필요 정보 크롤링
        columns = ['pid', 'country', 'nm', 'industry', 'sector', 'url', 'profile_url', 'financial_url', 'earnings_url', 'dividends_url']
        comp_info_list = obj.GetCompsInfo(columns, idx)

        for idx_comp, comp_info in comp_info_list.iterrows():
            '''
            # 요청이 너무 많은 경우 원격 호스트에 의해 강제로 끊는담.
            # 처리된 종목까지는 패스
            if option[1] == 'S&P 500' and idx_comp < 40:
                continue
            '''
            # 동일 종목이 기존에 처리된 지수에 중복 편입되어 있는 경우 패스
            if comp_info['pid'] in stocks_list:
                print(comp_info['nm'] + '는 이미 등록되어 있음.')
                continue
            else:
                stocks_list.append(comp_info['pid'])
                print("%s: %s, %s, %s, %s" % (idx_comp, comp_info['pid'], comp_info['nm'], country, group))

            # 종목의 산업과 업종 정보 크롤링
            comp_info = obj.GetProfileData(comp_info['profile_url'], comp_info)
            #print(comp_info)

            # 크롤링된 종목 정보를 DB 저장
            sql = "INSERT INTO stock_master (pid, country, nm, industry, sector, url, profile_url, financial_url, earnings_url, dividends_url, price_url, create_time, update_time)" \
                  "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', now(), now())" \
                  "ON DUPLICATE KEY UPDATE country='%s', nm='%s', industry='%s', sector='%s', url='%s', profile_url='%s', financial_url='%s'" \
                  ", earnings_url='%s', dividends_url='%s', price_url='%s', update_time = now()"
            sql_arg = (comp_info['pid'], option[0], comp_info['nm'], comp_info['industry'], comp_info['sector'], comp_info['url'], comp_info['profile_url'], comp_info['financial_url']
                       , comp_info['earnings_url'], comp_info['dividends_url'], comp_info['price_url']
                       , option[0], comp_info['nm'], comp_info['industry'], comp_info['sector'], comp_info['url'], comp_info['profile_url'], comp_info['financial_url']
                       , comp_info['earnings_url'], comp_info['dividends_url'], comp_info['price_url'])
            if (db.execute_query(sql, sql_arg) == False):
                print("stock_master insert error(%s: %s)" % (comp_info['pid'], comp_info['nm']))
            '''
            else:
                print('idx:\t' + str(idx_comp) + '\tnm\t' + comp_info['nm']
                      + '\tindustry\t' + comp_info['industry'] + '\tsector\t' + comp_info['sector']
                      + '\tpid\t' + comp_info['pid'] + '\turl\t' + comp_info['url']
                      + '\tprofile_url:\t' + comp_info['profile_url']
                      + '\tfinancial_url:\t' + comp_info['financial_url']
                      + '\tearnings_url:\t' + comp_info['earnings_url'])
            '''
            time.sleep(loop_sleep_term)

# 사전에 크롤링된 종목 정보를 DB에서 가져옴
else:
    sql = "SELECT pid, country, nm, industry, sector, url, profile_url, financial_url, earnings_url, dividends_url, price_url" \
          "  FROM stock_master"
    columns = ['pid', 'country', 'nm', 'industry', 'sector', 'url', 'profile_url', 'financial_url', 'earnings_url', 'dividends_url', 'price_url']
    comp_info_list = db.select_query(query=sql, columns=columns)

    # financial 정보 크롤링(anuual: 4년, qualterly: 4분기)
    if do_financial == True:
        for idx_comp, comp_info in comp_info_list.iterrows():
            '''
            # 정상 처리된 종목까지는 패스
            if idx_comp < 557:
                continue
            '''
            financials = obj.GetFinancialData(comp_info['financial_url'])
            #print(financials)

            component_list = ['Period Ending:', 'Period Length:', 'Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income', 'Total Assets', 'Total Liabilities', 'Total Equity', 'Cash From Operating Activities','Cash From Investing Activities', 'Cash From Financing Activities', 'Net Change in Cash']
            for term_type in financials:
                for idx_financial, financial_info in financials[term_type].iterrows():
                    #print(term_type + str(financial_info))

                    # 항목이 없는 경우 NULL로 채워야 sql 오류 없음
                    missing_components = set(component_list) - set(financial_info.index)
                    for component in missing_components:
                        financial_info[component] = 'NULL'

                    # 항목의 값이 없어 blank인 경우 NULL로 채워야 sql 오류 없음
                    for idx_null in np.where(financial_info.values == ''):
                        financial_info[idx_null] = 'NULL'

                    try:
                        sql = "INSERT INTO stock_financial (pid, date, term_type, period" \
                              ", total_revenue, gross_profit, operating_income, net_income" \
                              ", total_assets, total_liabilities, total_equity" \
                              ", cash_from_operating_activities, cash_from_investing_activities, cash_from_financing_activities, net_change_in_cash" \
                              ", create_time, update_time)" \
                              "VALUES ('%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())" \
                              "ON DUPLICATE KEY UPDATE total_revenue=%s, gross_profit=%s, operating_income=%s, net_income=%s" \
                              ", total_assets=%s, total_liabilities=%s, total_equity=%s" \
                              ", cash_from_operating_activities=%s, cash_from_investing_activities=%s, cash_from_financing_activities=%s, net_change_in_cash=%s" \
                              ", update_time = now()"
                        sql_arg = (comp_info['pid'], financial_info['Period Ending:'], term_type[0], financial_info['Period Length:']
                                   , financial_info['Total Revenue'], financial_info['Gross Profit'], financial_info['Operating Income'], financial_info['Net Income']
                                   , financial_info['Total Assets'], financial_info['Total Liabilities'], financial_info['Total Equity']
                                   , financial_info['Cash From Operating Activities'], financial_info['Cash From Investing Activities'], financial_info['Cash From Financing Activities'], financial_info['Net Change in Cash']
                                   , financial_info['Total Revenue'], financial_info['Gross Profit'], financial_info['Operating Income'], financial_info['Net Income']
                                   , financial_info['Total Assets'], financial_info['Total Liabilities'], financial_info['Total Equity']
                                   , financial_info['Cash From Operating Activities'], financial_info['Cash From Investing Activities'], financial_info['Cash From Financing Activities'], financial_info['Net Change in Cash'])
                        if (db.execute_query(sql, sql_arg) == False):
                            print("stock_financial insert error(%s: %s, %s, %s, %s)" % (comp_info['pid'], comp_info['nm'], term_type, financial_info['Period Ending:'], comp_info['financial_url']))
                    except:
                        print("stock_financial insert error(%s: %s, %s, %s, %s)" % (comp_info['pid'], comp_info['nm'], term_type, financial_info['Period Ending:'], comp_info['financial_url']))

            print("%s: %s, %s, %s, %s" % (idx_comp, comp_info['pid'], comp_info['nm'], idx_financial, comp_info['financial_url']))

            time.sleep(loop_sleep_term)

    # 실적(어닝) 정보 크롤링
    if do_earnings == True:
        for idx_comp, comp_info in comp_info_list.iterrows():
            '''
            # 정상 처리된 종목까지는 패스
            if idx_comp < 423:
                continue
            '''
            earnings_list = obj.GetEarningsData(comp_info['earnings_url'], loop_num=2)
            #print(earnings_list)

            for idx_earnings, earnings_info in earnings_list.iterrows():
                #print(earnings_info)

                # 항목의 값이 없어 blank인 경우 NULL로 채워야 sql 오류 없음
                for idx_null in np.where(earnings_info.values == 0.0):
                    earnings_info[idx_null] = 'NULL'

                try:
                    sql = "INSERT INTO stock_earnings (pid, date, period_end, eps_bold, eps_fore, revenue_bold, revenue_fore, create_time, update_time)" \
                          "VALUES ('%s', '%s', '%s', %s, %s, %s, %s, now(), now())" \
                          "ON DUPLICATE KEY UPDATE period_end='%s', eps_bold=%s, eps_fore=%s, revenue_bold=%s, revenue_fore=%s, update_time = now()"
                    sql_arg = (comp_info['pid'], earnings_info['release_date'], earnings_info['period_end']
                               , earnings_info['eps_bold'], earnings_info['eps_fore'], earnings_info['revenue_bold'], earnings_info['revenue_fore']
                               , earnings_info['period_end'], earnings_info['eps_bold'], earnings_info['eps_fore'], earnings_info['revenue_bold'], earnings_info['revenue_fore'])
                    if (db.execute_query(sql, sql_arg) == False):
                        print("stock_earnings insert error(%s: %s, %s, %s, %s)" % (comp_info['pid'], comp_info['nm'], earnings_info['release_date'], earnings_info['period_end'], comp_info['earnings_url']))

                except:
                    print("stock_earnings insert error(%s: %s, %s, %s, %s)" % (comp_info['pid'], comp_info['nm'], earnings_info['release_date'], earnings_info['period_end'], comp_info['earnings_url']))

            print("%s: %s, %s, %s, %s" % (idx_comp, comp_info['pid'], comp_info['nm'], idx_earnings, comp_info['earnings_url']))

            time.sleep(loop_sleep_term)

    # 배당 지급 정보 크롤링
    if do_dividends == True:
        for idx_comp, comp_info in comp_info_list.iterrows():
            '''
            # 정상 처리된 종목까지는 패스
            if idx_comp < 423:
                continue
            '''
            dividends_list = obj.GetDividendsData(comp_info['dividends_url'], loop_num=2)
            #print(dividends_list)

            for idx_dividends, dividends_info in dividends_list.iterrows():
                #print(dividends_info)

                try:
                    sql = "INSERT INTO stock_dividends (pid, ex_date, payment_date, dividend, yield, period, create_time, update_time)" \
                          "VALUES ('%s', '%s', '%s', %s, %s, '%s', now(), now())" \
                          "ON DUPLICATE KEY UPDATE payment_date='%s', dividend=%s, yield=%s, period='%s', update_time = now()"
                    sql_arg = (comp_info['pid'], dividends_info['ex_date'], dividends_info['payment_date']
                               , dividends_info['dividend'], dividends_info['yield'], dividends_info['period']
                               , dividends_info['payment_date'], dividends_info['dividend'], dividends_info['yield'], dividends_info['period'])
                    if (db.execute_query(sql, sql_arg) == False):
                        print("stock_dividends insert error(%s: %s, %s, %s, %s)" % (comp_info['pid'], comp_info['nm'], dividends_info['ex_date'], dividends_info['yield'], dividends_info['period']))

                except:
                    print("stock_dividends insert error(%s: %s, %s, %s, %s)" % (comp_info['pid'], comp_info['nm'], dividends_info['ex_date'], dividends_info['yield'], dividends_info['period']))

            print("%s: %s, %s, %s, %s" % (idx_comp, comp_info['pid'], comp_info['nm'], idx_dividends, comp_info['dividends_url']))

            time.sleep(loop_sleep_term)

    # 주가 데이 API
    if do_price == True:

        #obj.Finish()

        start_date = '1/1/2000'
        for idx_comp, comp_info in comp_info_list.iterrows():

            # 정상 처리된 종목까지는 패스
            if idx_comp < 139:
                continue

            # 기존 저장된 이후 주가부터 금일까지로 기간 설정
            check_sql = "SELECT MAX(date) as max_date FROM stock_price" \
                        " WHERE pid='%s'" % (comp_info['pid'])
            last_date = db.select_query(query=check_sql)
            if last_date[0][0] != None:
                start_date = last_date[0][0].split('-')
                start_date = str(int(start_date[1])) + '/' + str(int(start_date[2])) + '/' + str(int(start_date[0]))
            end_date = str(datetime.today().date()).split('-')
            end_date = str(int(end_date[1])) + '/' + str(int(end_date[2])) + '/' + str(int(end_date[0]))

            use_api = False
            if use_api == True:
                ihd = Investing.IndiceHistoricalData('https://www.investing.com/instruments/HistoricalDataAjax')

                header = {'name': comp_info['nm'],
                          'curr_id': comp_info['pid'],  # investing.com html에는 'key'로 조회
                          'sort_col': 'date',
                          'action': 'historical_data'}
                ihd.setFormData(header)

                # second set Variables
                ihd.updateFrequency('Daily')
                ihd.updateStartingEndingDate(start_date, end_date)
                ihd.setSortOreder('DESC')
                ihd.downloadData()
                #ihd.printData()
                prices = ihd.observations
            else:
                prices = obj.GetPriceData(comp_info['price_url'], set_calendar=True, start_date=start_date, end_date=end_date, t_gap=1.5)

            for price_idx, price in prices.iterrows():
                try:
                    pid = comp_info['pid']

                    if use_api == True:
                        p_date = price['Date'].replace(',', '').split()
                        p_date = str(date(int(p_date[2]), Investing.calendar_map[p_date[0]], int(p_date[1])))
                    else:
                        p_date = price['Date']
                    close = price['Price']
                    open = price['Open']
                    high = price['High']
                    low = price['Low']
                    if use_api == True:
                        value, unit = Investing.getRealValue(price['Vol.'])
                        vol = int(value * unit) if value != 'NULL' or unit != 'NULL' else 'NULL'
                    else:
                        vol = price['Vol.']
                    '''
                    # API를 통해 얻은 데이터의 기간이 설정보다 많은 데이터를 가지고 오는 경우 과거 데이터는 패스
                    if datetime.strptime(p_date, '%Y-%m-%d').date() <= datetime.strptime(start_date, '%m/%d/%Y').date():
                        break
                    '''
                    sql = "INSERT INTO stock_price (pid, date, close, open, high, low, vol, create_time, update_time) " \
                          "VALUES ('%s', '%s', %s, %s, %s, %s, %s, now(), now()) ON DUPLICATE KEY UPDATE close = %s, open = %s, high = %s, low = %s, vol = %s, update_time = now()"
                    sql_arg = (pid, p_date, close, open, high, low, vol, close, open, high, low, vol)

                    if (db.execute_query(sql, sql_arg) == False):
                        print("stock_price insert error(%s: %s, %s)" % (comp_info['pid'], comp_info['nm'], p_date))
                except (TypeError, KeyError) as e:
                    print('에러정보 : ', e, file=sys.stderr)

            print("%s: %s, %s, %s" % (idx_comp, comp_info['pid'], comp_info['nm'], price_idx))

            time.sleep(loop_sleep_term)

db.disconnect()

