# _*_ coding: utf-8 _*_

import os
import sys
import warnings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

import pandas as pd
import math
from datetime import datetime
from datetime import timedelta
from datetime import date
from itertools import count

from COMM import DB_Util
from COMM import File_Util
from COMM import CALC_Util


# Wrap운용팀 DB Connect
db = DB_Util.DB()
db.connet(host="127.0.0.1", port=3306, database="investing.com", user="root", password="ryumaria")


start_date = '2016-01-01'
sql = "SELECT a.pid AS pid" \
"     , a.date AS date" \
"     , a.eps_fore AS eps_fore" \
"     , a.eps_bold AS eps_bold" \
"     , a.revenue_fore AS revenue_fore" \
"     , a.revenue_bold AS revenue_bold" \
"     , (CASE @p_pid WHEN a.pid THEN @p_date ELSE @p_date:='' END) AS p_date" \
"     , (CASE @p_pid WHEN a.pid THEN format(@p_eps_fore,2) ELSE @p_eps_fore:=0 END) AS p_eps_fore" \
"     , (CASE @p_pid WHEN a.pid THEN format(@p_eps_bold,2) ELSE @p_eps_bold:=0 END) AS p_eps_bold" \
"     , (CASE @p_pid WHEN a.pid THEN format(@p_revenue_fore,0) ELSE @p_revenue_fore:=0 END) AS p_revenue_fore" \
"     , (CASE @p_pid WHEN a.pid THEN format(@p_revenue_bold,0) ELSE @p_revenue_bold:=0 END) AS p_revenue_bold" \
"     , (@p_pid:=a.pid)" \
"	 , (@p_date:=a.date)" \
"	 , (@p_eps_fore:=a.eps_fore)" \
"	 , (@p_eps_bold:=a.eps_bold)" \
"	 , (@p_revenue_fore:=a.revenue_fore)" \
"	 , (@p_revenue_bold:=a.revenue_bold)" \
"  FROM stock_earnings a, (select @p_pid:='', @p_date:='', @p_eps_fore:=0 , @p_eps_bold:=0 , @p_revenue_fore:=0, @p_revenue_bold:=0 from dual) b" \
" WHERE a.date > '%s'" % (start_date)

raw_data = db.select_query(query=sql)
raw_data.drop(columns=[11,12,13,14,15,16], inplace=True)
raw_data.columns = ['pid','date','eps_fore','eps_bold','revenue_fore','revenue_bold','p_date','p_eps_fore','p_eps_bold','p_revenue_fore','p_revenue_bold']
raw_data['acc_revenue_bold'] = 0.0
#print(raw_data)

pivoted_revenue_bold = raw_data.pivot(index='date', columns='pid', values='revenue_bold')
#print(pivoted_revenue_bold)
pivoted_revenue_fore = raw_data.pivot(index='date', columns='pid', values='revenue_fore')
#print(pivoted_revenue_fore)

is_new_pid = False
count_new_data = 0
arr_revenue_bold = [0.0]*4
for row in raw_data.iterrows():
    idx = row[0]
    data = row[1]

    arr_revenue_bold[:3] = arr_revenue_bold[-3:]

    if idx > 0:
        if data['pid'] == prev_pid:

            if is_new_pid == True:
                is_new_pid = False

        else:
            is_new_pid = True
            count_new_data = 0

    else:
        is_new_pid = True
        count_new_data = 0

    arr_revenue_bold[-1] = float(data['revenue_bold'] if data['revenue_bold'] != None else 0)

    count_new_data += 1

    if count_new_data >= 4:
        raw_data['acc_revenue_bold'][idx] = sum(arr_revenue_bold)/4

    prev_pid = data['pid']
    prev_revenue_bold = float(data['revenue_bold'] if data['revenue_bold'] != None else 0)

File_Util.SaveExcelFiles(obj_dict=raw_data)


db.disconnect()
