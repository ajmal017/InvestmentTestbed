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
from dateutil.relativedelta import relativedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

from COMM import DB_Util
from CRAWLING import Investing

def CrawlingData(index_nm_list, do_profile, do_financial, do_earnings, do_dividends, do_price_list, loop_sleep_term):
    obj = Investing.InvestingStockInfo(db)
    obj.Start(do_background=False)
    #time.sleep(15)

    # 주식의 기본 정보 크롤링
    if do_profile[0] == True:

        start_time = time.time()

        # 인덱스별로 중복복
        stocks_list = []

        # 기존에 등록되어 있는 종목은 pass
        sql = "SELECT pid FROM stock_master WHERE market IS NOT NULL and ticker IS NOT NULL"
        columns = ['pid']
        stocks_list += list(db.select_query(query=sql, columns=columns)['pid'])

        for idx, index_nm in enumerate(index_nm_list):

            # 대표지수에 포함되어 있는 종목 리스트 및 필요 정보 크롤링
            columns = ['pid', 'country', 'nm', 'ticker', 'industry', 'sector', 'market', 'url', 'profile_url', 'financial_url', 'earnings_url', 'dividends_url', 'price_url']
            comp_info_list = obj.GetCompListInIndex(index_nm, columns)

            for idx_comp, comp_info in comp_info_list.iterrows():

                # 요청이 너무 많은 경우 원격 호스트에 의해 강제로 끊는담.
                # 처리된 종목까지는 패스
                if idx_comp < do_profile[1]:
                    continue

                # 동일 종목이 기존에 처리된 지수에 중복 편입되어 있는 경우 패스
                if comp_info['pid'] in stocks_list:
                    print(comp_info['nm'] + '는 이미 등록되어 있음.')
                    continue
                else:
                    stocks_list.append(comp_info['pid'])
                    print("%s: %s, %s, %s" % (idx_comp, comp_info['pid'], comp_info['nm'], index_nm))

                # 종목의 산업과 업종 정보 크롤링
                comp_info = obj.GetProfileData(comp_info['profile_url'], comp_info)
                # 크롤링 된 데이터 예외처리
                for idx_null in np.where(comp_info.values == None):
                    comp_info[idx_null] = 'NULL'
                comp_info['nm'] = comp_info['nm'].replace("'", "")
                #print(comp_info)

                # 크롤링된 종목 정보를 DB 저장
                sql = "INSERT INTO stock_master (pid, country, nm, ticker, industry, sector, market, url, profile_url, financial_url, earnings_url, dividends_url, price_url, create_time, update_time)" \
                      "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', now(), now())" \
                      "ON DUPLICATE KEY UPDATE country='%s', nm='%s', ticker='%s', industry='%s', sector='%s', market='%s'" \
                      ", url='%s', profile_url='%s', financial_url='%s'" \
                      ", earnings_url='%s', dividends_url='%s', price_url='%s', update_time = now()"
                sql_arg = (comp_info['pid'], comp_info['country'], comp_info['nm'], comp_info['ticker'], comp_info['industry'], comp_info['sector'], comp_info['market']
                           , comp_info['url'], comp_info['profile_url'], comp_info['financial_url']
                           , comp_info['earnings_url'], comp_info['dividends_url'], comp_info['price_url']
                           , comp_info['country'], comp_info['nm'], comp_info['ticker'], comp_info['industry'], comp_info['sector'], comp_info['market']
                           , comp_info['url'], comp_info['profile_url'], comp_info['financial_url']
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

                end_time = time.time()
                if idx_comp % 30 == 0:
                    elapse_time = end_time - start_time
                    mins = int(elapse_time / 60)
                    secs = int(elapse_time % 60)
                    print('크롤링 프로파일: ' + str(mins) + 'mins ' + str(secs) + 'secs' + '(' + str(idx+1) + '/' + str(len(index_nm_list)) + ', ' + str(idx_comp+1) + '/' + str(len(comp_info_list)) + ')')


    # 사전에 크롤링된 종목 정보를 DB에서 가져옴
    else:
        sql = "SELECT pid, country, nm, industry, sector, url, profile_url, financial_url, earnings_url, dividends_url, price_url" \
              "  FROM stock_master" \
              " WHERE market in ('NASDAQ', 'NYSE')"
        columns = ['pid', 'country', 'nm', 'industry', 'sector', 'url', 'profile_url', 'financial_url', 'earnings_url', 'dividends_url', 'price_url']
        comp_info_list = db.select_query(query=sql, columns=columns)

        # financial 정보 크롤링(anuual: 4년, qualterly: 4분기)
        if do_financial[0] == True:

            start_time = time.time()

            for idx_comp, comp_info in comp_info_list.iterrows():

                # 정상 처리된 종목까지는 패스
                if idx_comp < do_financial[1]:
                    continue

                financials = obj.GetFinancialData(comp_info['financial_url'])
                #print(financials)

                component_list = ['Period Ending:', 'Period Length:', 'Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income', 'Total Assets', 'Total Liabilities', 'Total Equity', 'Cash From Operating Activities','Cash From Investing Activities', 'Cash From Financing Activities', 'Net Change in Cash']
                for term_type in financials:
                    idx_financial = 0
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

                print("%s: %s, %s, %s, %s" % (idx_comp, comp_info['pid'], comp_info['nm'], idx_financial+1, comp_info['financial_url']))

                time.sleep(loop_sleep_term)

                end_time = time.time()
                if idx_comp % 30 == 0:
                    elapse_time = end_time - start_time
                    mins = int(elapse_time / 60)
                    secs = int(elapse_time % 60)
                    print('크롤링 재무데이터: ' + str(mins) + 'mins ' + str(secs) + 'secs' + '(' + str(idx_comp + 1) + '/' + str(len(comp_info_list)) + ')')

        # 실적(어닝) 정보 크롤링
        if do_earnings[0] == True:

            start_time = time.time()

            for idx_comp, comp_info in comp_info_list.iterrows():

                # 정상 처리된 종목까지는 패스
                if idx_comp < do_earnings[2]:
                    continue

                earnings_list = obj.GetEarningsData(comp_info['earnings_url'], loop_num=do_earnings[1])
                #print(earnings_list)

                idx_earnings = 0
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

                print("%s: %s, %s, %s, %s" % (idx_comp, comp_info['pid'], comp_info['nm'], idx_earnings+1, comp_info['earnings_url']))

                time.sleep(loop_sleep_term)

                end_time = time.time()
                if idx_comp % 30 == 0:
                    elapse_time = end_time - start_time
                    mins = int(elapse_time / 60)
                    secs = int(elapse_time % 60)
                    print('크롤링 실적데이터: ' + str(mins) + 'mins ' + str(secs) + 'secs' + '(' + str(idx_comp + 1) + '/' + str(len(comp_info_list))  + ')')

        # 배당 지급 정보 크롤링
        if do_dividends[0] == True:

            start_time = time.time()

            for idx_comp, comp_info in comp_info_list.iterrows():

                # 정상 처리된 종목까지는 패스
                if idx_comp < do_dividends[2]:
                    continue

                dividends_list = obj.GetDividendsData(comp_info['dividends_url'], loop_num=do_dividends[1])
                #print(dividends_list)

                idx_dividends = 0
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

                print("%s: %s, %s, %s, %s" % (idx_comp, comp_info['pid'], comp_info['nm'], idx_dividends+1, comp_info['dividends_url']))

                time.sleep(loop_sleep_term)

                end_time = time.time()
                if idx_comp % 30 == 0:
                    elapse_time = end_time - start_time
                    mins = int(elapse_time / 60)
                    secs = int(elapse_time % 60)
                    print('크롤링 배당데이터: ' + str(mins) + 'mins ' + str(secs) + 'secs' + '(' + str(idx_comp + 1) + '/' + str(len(comp_info_list)) + ')')

        # 주가 데이 API
        if do_price_list[0] == True:

            start_time = time.time()
            #obj.Finish()

            start_date = '1/1/2000'
            for idx_comp, comp_info in comp_info_list.iterrows():

                # 정상 처리된 종목까지는 패스
                if idx_comp < do_price_list[3]:
                    continue

                # 기존 저장된 이후 주가부터 금일까지로 기간 설정
                check_sql = "SELECT MAX(date) as max_date FROM stock_price" \
                            " WHERE pid='%s'" % (comp_info['pid'])
                last_date = db.select_query(query=check_sql)
                # last_date[0][0]가 None인 경우는 해당 종목에 데이터가 하나도 없기 때문에 2000/1/1 이후 존제하는 모든 데이터를 수신  
                if last_date[0][0] != None:
                    start_date = last_date[0][0].split('-')
                    start_date = str(int(start_date[1])) + '/' + str(int(start_date[2])) + '/' + str(int(start_date[0]))
                # 금일까지 종가로 존제하는 모든 데이터를 수신
                end_date = str(datetime.today().date()).split('-')
                end_date = str(int(end_date[1])) + '/' + str(int(end_date[2])) + '/' + str(int(end_date[0]))

                # API를 이용해서 데이터 수신(수신되는 데이터가 완정하지 않음)
                if do_price_list[1] == True:
                    ihd = Investing.IndiceHistoricalData('https://www.investing.com/instruments/HistoricalDataAjax')
                    header = {'name': comp_info['nm'],
                              'curr_id': comp_info['pid'],  # investing.com html에서 'key'로 사용
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
                # 크롤링을 이용해서 데이터 수신.
                else:
                    prices = obj.GetPriceData(comp_info['price_url'], set_calendar=do_price_list[2], start_date=start_date, end_date=end_date)

                for price_idx, price in prices.iterrows():
                    try:
                        pid = comp_info['pid']

                        if do_price_list[1] == True:
                            
                            # API를 통해 데이터 제공되지 않는 종목 패스
                            if price['Date'] == 'No results found':
                                break

                            p_date = price['Date'].replace(',', '').split()
                            p_date = str(date(int(p_date[2]), Investing.calendar_map[p_date[0]], int(p_date[1])))

                            value, unit = Investing.getRealValue(price['Vol.'])
                            vol = int(value * unit) if value != 'NULL' or unit != 'NULL' else 'NULL'
                        else:
                            p_date = price['Date']
                            vol = price['Vol.']

                        close = price['Price']
                        open = price['Open']
                        high = price['High']
                        low = price['Low']

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

                # 비영업일 종가 전일 종가로 카피
                sql = "SELECT pid, date, close, open  FROM stock_price" \
                      " WHERE pid='%s'" % (comp_info['pid'])
                columns = ['pid', 'date', 'close', 'open']
                #print(sql % columns)

                p_data_list = db.select_query(query=sql, columns=columns)
                for p_data_idx, p_data in p_data_list.iterrows():
                    if p_data_idx > 0:
                        term = (datetime.strptime(p_data['date'], '%Y-%m-%d').date() - datetime.strptime(prev_date, '%Y-%m-%d').date()).days

                        if term > 1:
                            for n in range(term-1):
                                nonbis_date = str(datetime.strptime(prev_date, '%Y-%m-%d').date() + relativedelta(days=n+1))
                                sql = "INSERT INTO stock_price (pid, date, close, open) " \
                                      "VALUES ('%s', '%s', %s, %s) ON DUPLICATE KEY UPDATE close = %s, open = %s"
                                sql_arg = (comp_info['pid'], nonbis_date, prev_close, p_data['open'], prev_close, p_data['open'])
                                #print(sql % (sql_arg))
                                db.execute_query(sql, sql_arg)

                    prev_date = p_data['date']
                    prev_close = p_data['close']

                time.sleep(loop_sleep_term)

                end_time = time.time()
                if idx_comp % 30 == 0:
                    elapse_time = end_time - start_time
                    mins = int(elapse_time / 60)
                    secs = int(elapse_time % 60)
                    print('크롤링 가격데이터: ' + str(mins) + 'mins ' + str(secs) + 'secs' + '(' + str(idx_comp + 1) + '/' + str(len(comp_info_list)) + ')')

def GenerateAdditionalData():
    # 종목별 마지막 eps 데이터 조회
    sql_1 = " WITH tmp AS (SELECT c.pid AS pid, c.date AS date, c.eps_bold AS eps_bold, c.eps_fore AS eps_fore, c.p_date AS p_date" \
            "                   , c.chg_eps_bold AS chg_eps_bold, c.chg_eps_fore AS chg_eps_fore, c.num AS num" \
            "                FROM (SELECT a.pid AS pid, a.date AS date, a.eps_bold AS eps_bold, a.eps_fore AS eps_fore" \
            "                           , (CASE @p_pid WHEN a.pid THEN @rownum:=@rownum+1 ELSE @rownum:=1 END) num" \
            "                           , (CASE @p_pid WHEN a.pid THEN @p_date ELSE @p_date:='' END) p_date" \
            "                           , (CASE @p_pid WHEN a.pid THEN round(a.eps_bold/@p_eps_bold-1, 4) ELSE 0 END) chg_eps_bold" \
            "                           , (CASE @p_pid WHEN a.pid THEN round(a.eps_fore/@p_eps_fore-1, 4) ELSE 0 END) chg_eps_fore" \
            "                           , (@p_pid:=a.pid), (@p_date:=a.date), (@p_eps_bold:= a.eps_bold), (@p_eps_fore:= a.eps_fore)" \
            "                        FROM stock_earnings a, (SELECT @p_pid:='', @p_date:='', @p_eps_bold:=0, @p_eps_fore:=0, @rownum:=0 FROM DUAL) b" \
            "                       ORDER BY a.pid, a.date) c, stock_master d" \
            "               WHERE c.pid = d.pid)" \
            "SELECT a.*, c.date AS day, c.close AS close, c.close/a.eps_bold AS per_bold, round(c.close/a.eps_fore, 4) AS per_fore" \
            "  FROM tmp a, (SELECT pid AS pid, max(num) AS max_num FROM tmp GROUP BY pid) b, stock_price c" \
            " WHERE a.pid = b.pid AND a.num = b.max_num" \
            "   AND a.pid = c.pid AND c.date >= a.p_date AND c.date < a.date"
    result = db.select_query(query=sql_1)
    print(result)

if __name__ == '__main__':
    # Wrap운용팀 DB Connect
    db = DB_Util.DB()
    db.connet(host="127.0.0.1", port=3306, database="investing.com", user="root", password="ryumaria")

    #index_nm_list = ['NASDAQ Composite', 'KOSPI 200', 'KOSDAQ 150', 'S&P 500', 'Nasdaq 100', ]
    index_nm_list = ['NASDAQ Composite', 'United States all stocks', 'S&P 500', 'Nasdaq 100', ]
    # do_financial 0: 실행여부, 1: 시작 index
    # do_earnings 0: 실행여부, 1: 루프 num, 2: 시작 index
    # do_dividends 0: 실행여부, 1: 루프 num, 2: 시작 index
    # do_price_list 0: 실행여부, 1: API 사용여부, 2: Calendar 사용여부, 3: 시작 index
    CrawlingData(index_nm_list, do_profile=[True,0], do_financial=[False,0], do_earnings=[False,0,0], do_dividends=[False,0,0], do_price_list=[True,True,True,0], loop_sleep_term=1)
    #CrawlingData(options, do_profile=False, do_financial=False, do_earnings=False, do_dividends=True, do_price_list=[False, False, False], loop_sleep_term=0)
    GenerateAdditionalData()

    db.disconnect()

