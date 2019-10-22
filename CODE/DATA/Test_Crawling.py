# _*_ coding: utf-8 _*_

import os
import sys
import warnings
import time
import re
import copy

from datetime import datetime
from datetime import timedelta
from datetime import date
import pandas as pd
import numpy as np
import multiprocessing as mp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

from COMM import DB_Util
from CRAWLING import Investing

'''
import statsmodels.api as sm
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
'''
MULTI_PROCESS = False


# Wrap운용팀 DB Connect
db = DB_Util.DB()
db.connet(host="127.0.0.1", port=3306, database="investing.com", user="root", password="ryumaria")

# 등록된 Economic Event 리스트의 데이터를 크롤링
# Economic Event 리스트는 investing.com의 Economic Calendar에서 수집 후 엑셀 작업으로 DB에 insert
# 미국, 중국, 한국의 모든 이벤트
if 1:
    # Economic Event 리스트 select
    datas = db.select_query("SELECT cd, nm_us, link, ctry, period, type"
                            "  FROM economic_events"
                            " WHERE imp_us in (1,2,3)")
    datas.columns = ['cd', 'nm_us', 'link', 'ctry', 'period', 'type']
    # print(type(datas))

    # 병렬처리 개발중
    if MULTI_PROCESS == True:
        max_process_num = 2
        jobs = []

        # 병렬처리를 위해 datas를 datas_split array로 분할
        unit_size = int(len(datas)/max_process_num)+1
        for i in range(max_process_num):
            sub_datas = copy.deepcopy(datas[i*unit_size:min((i+1)*unit_size,len(datas))])
            print(i*unit_size,min((i+1)*unit_size,len(datas)))

            # chromedriver를 이용하여 session 연결
            session = Investing.InvestingEconomicEventCalendar(sub_datas, db)
            p = mp.Process(target=Investing.CrawlingStart, args=(session,))
            jobs.append(p)
            p.start()

            time.sleep(90)

        # Iterate through the list of jobs and remove one that are finished, checking every second.
        count_loop = 0
        while len(jobs) > 0:
            jobs = [job for job in jobs if job.is_alive()]
            print("%s: %s Process Left" % (count_loop, len(jobs)))
            time.sleep(10)

            count_loop += 1
    else:
        session = Investing.InvestingEconomicEventCalendar(datas, db)
        session.Start(t_gap=0.2, loop_num=3)



# 당일 Economic Event 리스트 크롤링
if 0:
    country_list = ['United States', 'South Korea', 'China', 'Euro Zone']
    i = crawling.InvestingEconomicCalendar('https://www.investing.com/economic-calendar/', country_list)
    i.getEvents()

# 각 국가별 지수 및 원자재 근월물 가격 데이터 크롤링
if 0:
    master_list = db.select_query("SELECT cd, nm_us, curr_id"
                                  "  FROM index_master")
    master_list.columns = ['cd', 'nm_us', 'curr_id']

    satrt_date = '9/1/2019'
    end_date = '9/24/2019'
    for master in master_list.iterrows():
        # first set Headers and FormData
        ihd = Investing.IndiceHistoricalData('https://www.investing.com/instruments/HistoricalDataAjax')

        header = {'name': master[1]['cd'],
                  'curr_id': master[1]['curr_id'], # investing.com html에는 'key'로 조회
                  'header': master[1]['nm_us'],
                  'sort_col': 'date',
                  'action': 'historical_data'}
        ihd.setFormData(header)

        # second set Variables
        ihd.updateFrequency('Daily')
        ihd.updateStartingEndingDate(satrt_date, end_date)
        ihd.setSortOreder('ASC')
        ihd.downloadData()
        ihd.printData()

        results = ihd.observations
        for result in results.iterrows():
            try:
                cd = master[1]['cd']

                date_rlt = result[1]['Date']
                date_splits = re.split('\W+', date_rlt)
                date_str = str(date(int(date_splits[2]), Investing.calendar_map[date_splits[0]], int(date_splits[1])))

                close = result[1]['Price']
                open = result[1]['Open']
                high = result[1]['High']
                low = result[1]['Low']

                value, unit = Investing.getRealValue(result[1]['Vol.'])
                vol = value * unit if value != 'NULL' or unit != 'NULL' else 'NULL'

                sql = "INSERT INTO index_price (idx_cd, date, close, open, high, low, vol, create_time, update_time) " \
                      "VALUES ('%s', '%s', %s, %s, %s, %s, %s, now(), now()) ON DUPLICATE KEY UPDATE close = %s, open = %s, high = %s, low = %s, vol = %s, update_time = now()"
                sql_arg = (cd, date_str, close, open, high, low, vol, close, open, high, low, vol)
                # print(sql % sql_arg)

                if (db.execute_query(sql, sql_arg) == False):
                    print(sql % sql_arg)
            except (TypeError, KeyError) as e:
                print('에러정보 : ', e, file=sys.stderr)
                print(date_splits, pre_statistics_time)
        # ihd.saveDataCSV()

if 0:
    datas = db.select_query("select a.nm_us, a.cd, b.release_date"
                            "  from economic_events a, economic_events_schedule b"
                            " where a.cd = b.event_cd"
                            "   and b.pre_release_yn = 0")
    datas.columns = ['nm_us', 'cd', 'release_date']

    last_nm_us = None
    last_cd = None
    last_release_date = None

    total_date = 0
    count = 0
    date_list = []
    for idx, data in enumerate(datas.iterrows()):
        try:
            curr_nm_us = data[1]['nm_us']
            curr_cd = data[1]['cd']
            curr_release_date = pd.to_datetime(str(data[1]['release_date']), format="%Y-%m-%d")

            if last_cd is not None:
                if last_cd != curr_cd or idx == datas.shape[0] - 1:
                    print(str(last_cd), '\t', last_nm_us, '\t', str(total_date / count), '\t',
                          str(sorted(date_list)[int(len(date_list) / 10)]), '\t',
                          str(sorted(date_list)[-int(len(date_list) / 10)]), '\t', str(len(date_list)))
                    total_date = 0
                    count = 0
                    date_list = []
                else:
                    days = (curr_release_date - last_release_date).days
                    total_date += days
                    count += 1
                    date_list.append(days)

            last_nm_us = curr_nm_us
            last_cd = curr_cd
            last_release_date = curr_release_date
        except ZeroDivisionError as e:
            print('에러정보 : ', str(last_cd), file=sys.stderr)
            print(str(last_cd), '\t', last_nm_us)

db.disconnect()
