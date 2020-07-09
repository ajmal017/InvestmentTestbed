# _*_ coding: utf-8 _*_

import os
import sys
import warnings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

import pandas as pd
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

PRINT_OUT_RAW_DATA_TO_FILE = True
# Economic Event 변동별 가격지표들의 수익률 비교
if 1:

    if PRINT_OUT_RAW_DATA_TO_FILE:
        raw_result_file = open("raw_result.txt", 'w')
    else:
        raw_result_file = sys.stdout

    # Futures를 이용하여 지수별 Price 데이터
    price_datas = db.select_query("select a.cd, b.date, b.open, b.close"
                                 "  from index_master a, index_price b"
                                 " where a.cd = b.idx_cd")
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
                                 #" where imp_us = 3"
                                 #"   and type = 'Ori'")
    event_datas.columns = ['nm', 'cd', 'unit']

    # Raw Data 로그
    raw_result_header = 'cd' + '\t' + 'nm' + '\t' + 'curr_date' + '\t' + 'diff' + '\t' + 'in_date' + '\t' + 'out_date'
    for pri_cd in pivoted_price_datas_close:
        raw_result_header = raw_result_header + '\t' + pri_cd
    raw_result_file.write(raw_result_header + '\n')


    # 지수 데이터가 존재하는 기간 이후 발생한 Economic Event 사용
    start_date = datetime.strptime('2010-02-01', '%Y-%m-%d').date()
    for event in event_datas.iterrows():
        nm = event[1]['nm']
        cd = event[1]['cd']
        unit = event[1]['unit']

        # Economic Event별 스케줄 데이터
        event_schedule_datas = db.select_query("select release_date, bold_value"
                                     "  from economic_events_schedule"
                                     " where pre_release_yn = 0"
                                     "   and event_cd = %s" % (cd))
        event_schedule_datas.columns = ['date', 'value']
        event_schedule_datas["change"] = None
        event_schedule_datas = event_schedule_datas.set_index('date')


        prev_date = None
        prev_value = None
        for schedule_idx, schedule_data in enumerate(event_schedule_datas.iterrows()):

            curr_date = datetime.strptime(schedule_data[0], '%Y-%m-%d').date()
            curr_value = schedule_data[1].value

            # 변화율을 계산하기 위해서 2번째 데이터부터 사용
            # 변화율을 계산하기 위해서 마지막에서 2번째 데이터까지 사용
            if schedule_idx > 0 and schedule_idx < event_schedule_datas.shape[0]-1:
                # Prcie 데이터가 존재하기 시작한 이후 발표된 Economic Event 데이터
                if curr_date > start_date:
                    # 단위가 %인 경우 차분을 사용, 그렇지 않은 경우 변화율을 사용
                    diff = CALC_Util.getEconomicDiff(curr_value, prev_value, unit)
                    if diff is not None:
                        event_schedule_datas['change'][schedule_idx] = diff
                    raw_result_body = str(cd) + '\t' + nm + '\t' + str(curr_date) + '\t' + str(diff)

                    # 가격지표(Index)별 경제지표 발표에 의한 수익률 확인
                    for price_idx, price_cd in enumerate(pivoted_price_datas_close):
                        # 모든 가격지표에 동일한 진입 청산일 적용
                        if price_idx == 0:
                            # 경제지표 발표 익일 포지션 진입
                            for check_point in range(0, len(price_datas_date_list), 1):
                                if price_datas_date_list[check_point] > curr_date:
                                    in_date = price_datas_date_list[check_point]
                                    raw_result_body = raw_result_body + '\t' + str(in_date)
                                    break

                            # 다음 결제지표 발표 전일 포지션 청산
                            next_date = datetime.strptime(event_schedule_datas.index[schedule_idx+1], '%Y-%m-%d').date()
                            for check_point in range(len(price_datas_date_list)-1, 0, -1):
                                if price_datas_date_list[check_point] < next_date:
                                    out_date = price_datas_date_list[check_point]
                                    raw_result_body = raw_result_body + '\t' + str(out_date)
                                    break

                        try:
                            in_value = pivoted_price_datas_open[price_cd][str(in_date)]
                            out_vlaue = pivoted_price_datas_close[price_cd][str(out_date)]
                            ratio = out_vlaue/in_value-1
                        except (KeyError) as e:
                            print('에러정보 : ', e, file=sys.stderr)
                            print(cd, nm, price_cd, curr_date, in_date, out_date)

                        sql = "INSERT INTO economic_events_results (event_cd, event_nm, index_cd, event_date" \
                              ", position_in_date, position_out_date, position_in_value, position_out_value, event_value_diff, index_value_ratio) " \
                              "VALUES (%s, '%s', '%s', '%s', '%s', '%s', %s, %s, %s, %s) ON DUPLICATE KEY UPDATE event_value_diff = %s, index_value_ratio = %s"
                        sql_arg = (cd, nm, price_cd, str(curr_date), str(in_date), str(out_date), in_value, out_vlaue, diff, ratio, diff, ratio)
                        #print(sql % sql_arg)

                        if (db.execute_query(sql, sql_arg) == False and math.isnan(ratio) == False):
                            print(sql % sql_arg)

                        raw_result_body = raw_result_body + '\t' + str(ratio)
                    raw_result_file.write(raw_result_body + '\n')

            prev_date = curr_date
            prev_value = curr_value

    if PRINT_OUT_RAW_DATA_TO_FILE:
        raw_result_file.close()

db.disconnect()
