# _*_ coding: utf-8 _*_

import ta

import os
import sys
import warnings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

import pandas as pd


class TechnicalAnalysis(object):

    def __init__(self, data, window_size):
        self.data = data
        self.window_size = window_size


    def getDatas(self):
        return None

class BollingerBand(TechnicalAnalysis):

    def __init__(self, data, window_size=20, sigma_size=2):
        super().__init__(data, window_size)
        self.sigma_size = sigma_size
        self.hband = None
        self.lband = None

    def getDatas(self):

        self.hband = ta.bollinger_hband(self.data, self.window_size, self.sigma_size)
        self.lband = ta.bollinger_lband(self.data, self.window_size, self.sigma_size)

        bol_bands = self.data.to_frame(name='value')
        bol_bands['hband'] = self.hband
        bol_bands['lband'] = self.lband

        return bol_bands

class RSI(TechnicalAnalysis):

    def __init__(self, data, window_size=14):
        super().__init__(data, window_size)
        self.score = None

    def getDatas(self):
        self.score = ta.rsi(self.data, self.window_size)

        return self.score

class MACD(TechnicalAnalysis):

    def __init__(self, data, swindow_size=12, lwindow_size=26):
        super().__init__(data, swindow_size)
        self.swindow_size = swindow_size
        self.lwindow_size = lwindow_size
        self.score = None

    def getDatas(self):
        self.score = ta.macd(self.data, self.swindow_size, self.lwindow_size)

        return self.score
