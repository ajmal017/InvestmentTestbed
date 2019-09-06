# _*_ coding: utf-8 _*_

import matplotlib.pyplot as plt
import pandas as pd



class Figure(object):

    def __init__(self):
        self.data = None

    def draw(self, data=None, title=""):
        self.data = data
        if self.data is None:
            return False

        self.data.plot()
        plt.title(title)
        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.show()