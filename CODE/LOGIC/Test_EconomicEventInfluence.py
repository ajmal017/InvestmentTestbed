# _*_ coding: utf-8 _*_

import os
import sys
import warnings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

import pandas as pd

from COMM import DB_Util


# Wrap운용팀 DB Connect
db = DB_Util.DB()
db.connet(host="127.0.0.1", port=3306, database="investing.com", user="root", password="ryumaria")

if 1:
    price_list = db.select_query("select a.cd, b.date, b.close"
                                 "  from index_master a, index_price b"
                                 " where a.cd = b.idx_cd")
    price_list.columns = ['cd', 'date', 'value']

    price_list["dateT"] = price_list['date'].apply(lambda x: pd.to_datetime(str(x), format="%Y-%m-%d"))
    reference_list = price_list.resample('B', on='dateT', convention='end')
    reference_datas = price_list.loc[price_list['dateT'].isin(list(reference_list.indices))]
    pivoted_reference_datas = reference_datas.pivot(index='date', columns='cd', values='value').fillna(method='ffill')

    event_list = db.select_query("select nm_us, cd"
                                 "  from economic_events"
                                 " where imp_us = 3")
    event_list.columns = ['nm', 'cd']

    for event in event_list.iterrows():
        nm = event[1]['nm']
        cd = event[1]['cd']
        #print(nm, cd)

        schedule_list = db.select_query("select release_date, bold_value"
                                     "  from economic_events_schedule"
                                     " where pre_release_yn = 0"
                                     "   and event_cd = %s" % (cd))
        schedule_list.columns = ['date', 'value']

        prev_date = None
        prev_value = None
        for idx, data in enumerate(schedule_list.set_index('date').iterrows()):

            date = data[0]
            value = data[1].value

            if idx > 0:
                if value >= 0 and prev_date >= 0:
                    pass
                elif value < 0 and prev_date < 0:
                    pass
                elif value >= 0 and prev_date < 0:
                    pass
                elif value < 0 and prev_date >= 0:
                    pass

            prev_date = date
            prev_value = value













db.disconnect()
