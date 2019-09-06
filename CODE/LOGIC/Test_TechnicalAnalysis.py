# _*_ coding: utf-8 _*_

import os
import sys
import warnings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

import pandas as pd

from COMM import DB_Util
from COMM import Figure_Util
from COMM import TechnicalAnalysis_Util


# Wrap운용팀 DB Connect
db = DB_Util.DB()
db.connet(host="127.0.0.1", port=3306, database="investing.com", user="root", password="ryumaria")

if 1:

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

    for cd in pivoted_price_datas_close:
        data = pivoted_price_datas_close[cd][-500:]

        # pandas의 series를 input data 형태로 사용
        analysis = TechnicalAnalysis_Util.BollingerBand(data)
        analysis_datas = analysis.getDatas()

        analysis = TechnicalAnalysis_Util.RSI(data)
        analysis_datas['rsi'] = analysis.getDatas()

        analysis = TechnicalAnalysis_Util.MACD(data)
        analysis_datas['macd'] = analysis.getDatas()

        panel = Figure_Util.Figure()
        panel.draw(analysis_datas, title=cd, subplots=['rsi', 'macd'], figsize=(20,10))

db.disconnect()

