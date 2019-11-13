# _*_ coding: utf-8 _*_

import os
import sys
import warnings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

import datetime
import math
import pandas as pd
import numpy as np
import seaborn as sns

from hmmlearn.hmm import MultinomialHMM

from COMM import DB_Util
from COMM import Figure_Util
from COMM import TechnicalAnalysis_Util


if __name__ == "__main__":

    # Wrap운용팀 DB Connect
    db = DB_Util.DB()
    db.connet(host="127.0.0.1", port=3306, database="investing.com", user="root", password="ryumaria")

    # Futures를 이용하여 지수별 Price 데이터 로드
    idx_nm = 'SPX'
    law_data = db.select_query("select b.date, b.open, b.close"
                                  "  from index_master a, index_price b"
                                  " where a.cd = b.idx_cd"
                                  "   and a.cd = '%s'"% (idx_nm))
    law_data.columns = ['date', 'open', 'close']

    # date를 index로 설정
    law_data = law_data.set_index(law_data['date'], inplace=False)
    law_data = law_data.drop(columns=['date'], inplace=False)


    # BollingerBand 데이터 생성
    analysis = TechnicalAnalysis_Util.BollingerBand(data=law_data['close'], window_size=20, sigma_size=1)
    analysis_data = analysis.getDatas()

    # lowwer band 아래 있으면 1, 아니면 0
    analysis_data['bb_v'] = 0
    for i, values in enumerate(zip(analysis_data['value'], analysis_data['lband'])):
        if values[0] < values[1]:
            analysis_data['bb_v'][i] = 1


    # RSI 데이터 생성
    analysis = TechnicalAnalysis_Util.RSI(law_data['close'])
    analysis_data['rsi'] = analysis.getDatas()

    # 30보다 작으면 1, 아니면 0
    analysis_data['rsi_v'] = 0
    for i, value in enumerate(analysis_data['rsi']):
        if value < 40:
            analysis_data['rsi_v'][i] = 1


    # MACD 데이터 생성
    analysis = TechnicalAnalysis_Util.MACD(data=law_data['close'], swindow_size=12, lwindow_size=26)
    analysis_data['macd'] = analysis.getDatas()

    # MACD는 전일대비 +이면 1, 아니면 0
    analysis_data['macd_v'] = 0
    for i in range(1, len(analysis_data['macd'])):
        if analysis_data['macd'][i] > analysis_data['macd'][i-1]:
            analysis_data['macd_v'][i] = 1


    # 기술적분석 시그널 Lag 적용
    obs_lag = 1
    analysis_data['bb_v'] = analysis_data['bb_v'].shift(obs_lag)
    analysis_data['rsi_v'] = analysis_data['rsi_v'].shift(obs_lag)
    analysis_data['macd_v'] = analysis_data['macd_v'].shift(obs_lag)

    # 기술적분석 데이터 삭제
    analysis_data = analysis_data.drop(columns=['hband'], inplace=False)
    analysis_data = analysis_data.drop(columns=['lband'], inplace=False)
    analysis_data = analysis_data.drop(columns=['rsi'], inplace=False)
    analysis_data = analysis_data.drop(columns=['macd'], inplace=False)

    analysis_data['return'] = analysis_data['value'].pct_change()
    analysis_data = analysis_data.dropna(axis = 0)
    analysis_data['v'] = (analysis_data['bb_v'] + analysis_data['rsi_v'] + analysis_data['macd_v']).astype(int)




    # 학습데이터와 테스트데이터를 나눈다
    split_point = int(len(analysis_data) * 0.8)
    train_data = analysis_data[:split_point]
    test_data = analysis_data[split_point:]


    # up = 0, down = 1
    states = ["up", "down"]
    n_states = len(states)

    observations = ["0", "1", "2", "3"]
    n_observations = len(observations)

    # hmm 파라미터 설정
    start_probability = np.array([0.0, 0.0])
    start_probability[0] = sum(1 for e in train_data['return'] if e >= 0.0) / len(train_data)
    start_probability[1] = sum(1 for e in train_data['return'] if e < 0.0) / len(train_data)

    transition_probability = np.array([[0.0,0.0],[0.0,0.0]])
    for i in range(1, len(train_data)):
        if train_data['return'][i-1] >= 0.0 and train_data['return'][i] >= 0.0:
            transition_probability[0][0] += 1
        if train_data['return'][i-1] >= 0.0 and train_data['return'][i] < 0.0:
            transition_probability[0][1] += 1
        if train_data['return'][i-1] < 0.0 and train_data['return'][i] >= 0.0:
            transition_probability[1][0] += 1
        if train_data['return'][i-1] < 0.0 and train_data['return'][i] < 0.0:
            transition_probability[1][1] += 1
    transition_probability[0] /= sum(1 for e in train_data['return'][:-1] if e >= 0.0)
    transition_probability[1] /= sum(1 for e in train_data['return'][:-1] if e < 0.0)
    #print(transition_probability)

    emission_probability = np.array([[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0]])
    for i in range(len(train_data)):
        if train_data['return'][i] >= 0.0 and analysis_data['v'][i] == 0:
            emission_probability[0][0] += 1
        if train_data['return'][i] >= 0.0 and analysis_data['v'][i] == 1:
            emission_probability[0][1] += 1
        if train_data['return'][i] >= 0.0 and analysis_data['v'][i] == 2:
            emission_probability[0][2] += 1
        if train_data['return'][i] >= 0.0 and analysis_data['v'][i] == 3:
            emission_probability[0][3] += 1
        if train_data['return'][i] < 0.0 and analysis_data['v'][i] == 0:
            emission_probability[1][0] += 1
        if train_data['return'][i] < 0.0 and analysis_data['v'][i] == 1:
            emission_probability[1][1] += 1
        if train_data['return'][i] < 0.0 and analysis_data['v'][i] == 2:
            emission_probability[1][2] += 1
        if train_data['return'][i] < 0.0 and analysis_data['v'][i] == 3:
            emission_probability[1][3] += 1
    emission_probability[0] /= sum(1 for e in train_data['return'] if e >= 0.0)
    emission_probability[1] /= sum(1 for e in train_data['return'] if e < 0.0)
    #print(emission_probability)


    hmm = MultinomialHMM(n_components=n_states)
    hmm.startprob = start_probability
    hmm.transmat = transition_probability
    hmm.emissionprob = emission_probability

    bob_says = np.array([[0, 2, 1, 1, 2, 0]]).T
    hmm = hmm.fit(bob_says)

    logprob, alice_hears = hmm.decode(bob_says, algorithm="viterbi")
    print("Bob says:", ", ".join(map(lambda x: observations[x], bob_says)))
    print("Alice hears:", ", ".join(map(lambda x: states[x], alice_hears)))



    '''
    law_data['hmm_states'] = hmm.predict(rets)
    panel = Figure_Util.Figure()
    panel.draw(law_data, title='close', subplots=['hmm_states'], figsize=(20, 10))
    '''

    db.disconnect()

