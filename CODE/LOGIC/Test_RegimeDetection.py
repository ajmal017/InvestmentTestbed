# _*_ coding: utf-8 _*_

import os
import sys
import warnings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

import datetime
import pickle
import pandas as pd
import numpy as np
import seaborn as sns

from hmmlearn.hmm import MultinomialHMM
from matplotlib import cm, pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator

from COMM import DB_Util
from COMM import Figure_Util




if __name__ == "__main__":

    # Wrap운용팀 DB Connect
    db = DB_Util.DB()
    db.connet(host="127.0.0.1", port=3306, database="investing.com", user="root", password="ryumaria")

    # Futures를 이용하여 지수별 Price 데이터
    idx_nm = 'SPX'
    spy = db.select_query("select b.date, b.open, b.close"
                                  "  from index_master a, index_price b"
                                  " where a.cd = b.idx_cd"
                                  "   and a.cd = '%s'"% (idx_nm))
    spy.columns = ['date', 'open', 'close']
    spy.set_index(spy['date'], inplace=True)
    spy.drop(columns=['date'], inplace=True)
    spy['Returns'] = spy['close'].pct_change()
    spy.dropna(inplace=True)
    rets = np.column_stack([spy["Returns"]])


    states = ["up", "down"]
    n_states = len(states)

    observations = ["rsi", "macd", "cross"]
    n_observations = len(observations)

    start_probability = np.array([0.65, 0.35])

    transition_probability = np.array([
        [0.7, 0.3],
        [0.4, 0.6]
    ])

    emission_probability = np.array([
        [0.1, 0.4, 0.5],
        [0.6, 0.3, 0.1]
    ])


    hmm = MultinomialHMM(n_components=n_states)
    hmm.startprob = start_probability
    hmm.transmat = transition_probability
    hmm.emissionprob = emission_probability

    bob_says = [0, 2, 1, 1, 2, 0]
    hmm = hmm.fit(bob_says)
    logprob, alice_hears = hmm.decode(bob_says, algorithm="viterbi")
    print("Bob says:", ", ".join(map(lambda x: observations[x], bob_says)))
    print("Alice hears:", ", ".join(map(lambda x: states[x], alice_hears)))


    print("Model Score:", hmm.score(rets))

    for i in range(hmm.n_components):
        print('''Hidden state {:2} -  Mean : {:.3f} \\ Variance : {:.3f}'''.format(i + 1, hmm.means_[i][0], np.diag(hmm.covars_[i])[0]))

    spy['hmm_states'] = hmm.predict(rets)
    panel = Figure_Util.Figure()
    panel.draw(spy, title='close', subplots=['hmm_states'], figsize=(20, 10))

    db.disconnect()

