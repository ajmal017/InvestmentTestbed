# _*_ coding: utf-8 _*_

import os
import sys
import warnings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from datetime import date
from itertools import count
import math

from COMM import DB_Util
from COMM import CALC_Util


# Wrap운용팀 DB Connect
db = DB_Util.DB()
db.connet(host="127.0.0.1", port=3306, database="investing.com", user="root", password="ryumaria")

PRINT_OUT_RAW_DATA_TO_FILE = False
# Economic Event 변동별 가격지표들의 수익률 비교
if 1:

    if PRINT_OUT_RAW_DATA_TO_FILE:
        raw_result_file = open("raw_result.txt", 'w')
    else:
        raw_result_file = sys.stdout

    # 지수 데이터가 존재하는 기간 이후 발생한 Economic Event 사용
    start_date = '2010-01-01'

    # Futures를 이용하여 지수별 Price 데이터
    # 금리 & 통화 데이터는 제
    price_datas = db.select_query("select a.cd, b.date, b.open, b.close"
                                 "  from index_master a, index_price b"
                                 " where a.cd = b.idx_cd"
                                  "  and a.type not in ('R','C')"
                                 "   and b.date > '%s'" % (start_date))
    price_datas.columns = ['cd', 'date', 'open', 'close']

    price_datas["dateT"] = price_datas['date'].apply(lambda x: pd.to_datetime(str(x), format="%Y-%m-%d"))
    resample_list = price_datas.resample('B', on='dateT', convention='end')
    sampled_price_datas = price_datas.loc[price_datas['dateT'].isin(list(resample_list.indices))]
    pivoted_price_datas_close = sampled_price_datas.pivot(index='date', columns='cd', values='close').fillna(method='ffill')
    pivoted_price_datas_open = sampled_price_datas.pivot(index='date', columns='cd', values='open').fillna(method='ffill')

    # 지수 데이터가 정리된 Price 데이터가 존재하는 date 리스트
    price_datas_date_list = [datetime.strptime(x, '%Y-%m-%d').date() for x in pivoted_price_datas_open.index]

    # Economic Event 리스트
    event_datas = db.select_query("select nm_us, cd, unit"
                                 "  from economic_events")
                                 #" where cd = 75")
                                 #" where imp_us = 3"
                                 #"   and type = 'Ori'")
    event_datas.columns = ['nm', 'cd', 'unit']

    # Raw Data 로그
    raw_result_header = 'cd' + '\t' + 'nm' + '\t' + 'curr_date' + '\t' + 'diff' + '\t' + 'in_date' + '\t' + 'out_date'
    for pri_cd in pivoted_price_datas_close:
        raw_result_header = raw_result_header + '\t' + pri_cd
    #raw_result_file.write(raw_result_header + '\n')


    for event in event_datas.iterrows():
        nm = event[1]['nm']
        cd = event[1]['cd']
        unit = event[1]['unit']

        # Economic Event별 스케줄 데이터
        event_schedule_datas = db.select_query("select release_date, bold_value"
                                     "  from economic_events_schedule"
                                     " where pre_release_yn = 0"
                                     "   and event_cd = %s"
                                     "   and release_date > '%s'" % (cd, start_date))
        event_schedule_datas.columns = ['date', 'value']
        event_schedule_datas['prev'] = None
        event_schedule_datas['curr'] = None
        event_schedule_datas['diff'] = None
        event_schedule_datas = event_schedule_datas.set_index('date')


        prev_date = None
        prev_value = None
        for schedule_idx, schedule_data in enumerate(event_schedule_datas.iterrows()):

            curr_date = datetime.strptime(schedule_data[0], '%Y-%m-%d').date()
            curr_value = schedule_data[1]['value']

            # 변화율을 계산하기 위해서 2번째 데이터부터 사용
            if schedule_idx > 0:
                diff = round(curr_value - prev_value, 5)
                if diff is not None:
                    event_schedule_datas['prev'][schedule_idx] = prev_value
                    event_schedule_datas['curr'][schedule_idx] = curr_value
                    event_schedule_datas['diff'][schedule_idx] = round(diff, 5)
                raw_result_body = str(cd) + '\t' + nm + '\t' + str(curr_date) + '\t' + str(diff)

            prev_date = curr_date
            prev_value = curr_value

        # diff의 z-score를 이용하여 영향도 파
        window_size = 3
        event_schedule_datas['std'] = event_schedule_datas['diff'].rolling(window_size).std()
        event_schedule_datas['mean'] = event_schedule_datas['diff'].rolling(window_size).mean()
        event_schedule_datas['z-score'] = None
        for schedule_idx, schedule_data in enumerate(event_schedule_datas.iterrows()):
            try:
                event_schedule_datas['z-score'][schedule_idx] = round((event_schedule_datas['diff'][schedule_idx] - event_schedule_datas['mean'][schedule_idx]) / event_schedule_datas['std'][schedule_idx], 5)
            except:
                #print(nm + '\t' + schedule_data[0])
                event_schedule_datas['z-score'][schedule_idx] = math.nan


        # 가격지표(Index)별 경제지표 발표 후 값 변화 확인
        index_datas = pd.DataFrame(index=event_schedule_datas.index)
        index_datas['in_date'] = None
        index_datas['out_date'] = None
        for price_idx, price_cd in enumerate(pivoted_price_datas_close):

            index_datas[price_cd+'in_value'] = None
            index_datas[price_cd+'out_value'] = None
            index_datas[price_cd+'diff'] = None
            for schedule_idx, schedule_data in enumerate(event_schedule_datas.iterrows()):

                if schedule_idx < event_schedule_datas.shape[0]-1:

                    event_date = datetime.strptime(event_schedule_datas.index[schedule_idx], '%Y-%m-%d').date()
                    next_event_date = datetime.strptime(event_schedule_datas.index[schedule_idx + 1], '%Y-%m-%d').date()

                    # 모든 가격지표에 동일한 진입 청산일 적용
                    # 반복작업을 하지 않기 위해...
                    if price_idx == 0:
                        # 경제지표 발표 익일 포지션 진입
                        for curr_date in price_datas_date_list:
                            if curr_date > event_date:
                                index_datas['in_date'][schedule_idx] = curr_date
                                raw_result_body = raw_result_body + '\t' + str(curr_date)
                                break

                        # 다음 결제지표 발표 전일 포지션 청산

                        for curr_date in reversed(price_datas_date_list):
                            if curr_date < next_event_date:
                                index_datas['out_date'][schedule_idx] = curr_date
                                raw_result_body = raw_result_body + '\t' + str(curr_date)
                                break
                    try:
                        in_date = str(index_datas['in_date'][schedule_idx])
                        out_date = str(index_datas['out_date'][schedule_idx])

                        index_datas[price_cd+'in_value'][schedule_idx] = pivoted_price_datas_open[price_cd][in_date]
                        index_datas[price_cd+'out_value'][schedule_idx] = pivoted_price_datas_close[price_cd][out_date]
                        index_datas[price_cd+'diff'][schedule_idx] = round(index_datas[price_cd+'out_value'][schedule_idx] - index_datas[price_cd+'in_value'][schedule_idx], 5)
                    except (KeyError) as e:
                        print('에러정보 : ', e, file=sys.stderr)
                        print(cd, nm, price_cd, curr_date, index_datas['in_date'][schedule_idx], index_datas['out_date'][schedule_idx])

                    raw_result_body = raw_result_body + '\t' + str(index_datas[price_cd+'in_value'][schedule_idx]) + '\t' + str(index_datas[price_cd+'out_value'][schedule_idx])
                #raw_result_file.write(raw_result_body + '\n')


        for price_idx, price_cd in enumerate(pivoted_price_datas_close):
            index_datas[price_cd+'std'] = index_datas[price_cd+'diff'].rolling(window_size).std()
            index_datas[price_cd+'mean'] = index_datas[price_cd+'diff'].rolling(window_size).mean()
            index_datas[price_cd+'z-score'] = None
            for schedule_idx, schedule_data in enumerate(event_schedule_datas.iterrows()):
                try:
                    index_datas[price_cd+'z-score'][schedule_idx] = round((index_datas[price_cd+'diff'][schedule_idx] - index_datas[price_cd+'mean'][schedule_idx]) / index_datas[price_cd+'std'][schedule_idx], 5)
                except:
                    index_datas[price_cd+'z-score'][schedule_idx] = math.nan


        # 분석을 위해 DB에 데이터 저장
        for price_idx, price_cd in enumerate(pivoted_price_datas_close):

            start_point = 0
            for idx, data in enumerate(index_datas[price_cd+'diff']):
                if math.isnan(data) == False:
                    start_point = idx
                    break

            directoin = 1 if np.corrcoef(list(index_datas[price_cd+'diff'].values[start_point+1:-1]), list(event_schedule_datas['diff'].values[start_point+1:-1]))[0][1] > 0.0 else -1
            for schedule_idx, schedule_data in enumerate(event_schedule_datas.iterrows()):
                sql = "INSERT INTO economic_events_results (event_cd, index_cd, event_date" \
                      ", position_in_date, position_out_date, in_value, out_value, value_diff, prev_event, curr_event, event_diff, direction) " \
                      "VALUES (%s, '%s', '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, %s) " \
                      "ON DUPLICATE KEY UPDATE in_value=%s, out_value=%s, value_diff=%s, prev_event=%s, curr_event=%s, event_diff=%s, direction=%s"
                sql_arg = (cd, price_cd, schedule_data[0], index_datas['in_date'][schedule_idx], index_datas['out_date'][schedule_idx]
                           , index_datas[price_cd+'in_value'][schedule_idx], index_datas[price_cd+'out_value'][schedule_idx], index_datas[price_cd+'diff'][schedule_idx]
                           , event_schedule_datas['prev'][schedule_idx], event_schedule_datas['curr'][schedule_idx], event_schedule_datas['diff'][schedule_idx], directoin
                           , index_datas[price_cd+'in_value'][schedule_idx], index_datas[price_cd+'out_value'][schedule_idx], index_datas[price_cd+'diff'][schedule_idx]
                           , event_schedule_datas['prev'][schedule_idx], event_schedule_datas['curr'][schedule_idx], event_schedule_datas['diff'][schedule_idx], directoin)
                #print(sql % sql_arg)

                if (db.execute_query(sql, sql_arg) == False):
                    #print(sql % sql_arg)
                    pass


    if PRINT_OUT_RAW_DATA_TO_FILE:
        raw_result_file.close()

db.disconnect()
