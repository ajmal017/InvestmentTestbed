# _*_ coding: utf-8 _*_

import random

import matplotlib.pyplot as plt
import pandas as pd



class Figure(object):

    def __init__(self):
        self.data = None
        self.figsize = None

    def draw(self, data=None, title="", subplots=None, figsize=(10,10)):
        self.data = data
        if self.data is None:
            return False

        self.figsize = figsize

        ax = {}
        fig, ax['base'] = plt.subplots()
        ax['base'].set_ylabel('base')
        for idx, subplot_nm in enumerate(subplots):
            ax[subplot_nm] = ax['base'].twinx()
            ax[subplot_nm].set_ylabel(subplot_nm)

            if idx > 0:
                rspine = ax[subplot_nm].spines['right']
                rspine.set_position(('axes', 1.05 * idx))
                ax[subplot_nm].set_frame_on(True)
                ax[subplot_nm].patch.set_visible(False)
                fig.subplots_adjust(right=0.75 * idx)

        #self.data.plot(figsize=(20, 10))
        for cd in self.data:
            if cd not in subplots:
                self.data[cd].plot(ax=ax['base'], figsize=self.figsize)
            else:
                for subplot_nm in subplots:
                    if cd == subplot_nm:
                        r = lambda: random.randint(0, 255)
                        self.data[cd].plot(ax=ax[cd], figsize=self.figsize, style=('#%02X%02X%02X' % (r(), r(), r())))

        plt.title(title)
        plt.show()


