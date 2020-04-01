

import os
import sys
import warnings

import pylab
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
from pandas import *


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.filterwarnings("ignore")

pylab.rcParams['figure.figsize'] = (10, 6)

# Calculates portfolio mean return
def port_mean(W, R):
    return sum(R * W)

# Calculates portfolio variance of returns
def port_var(W, C):
    return np.dot(np.dot(W, C), W)

# Combination of the two functions above - mean and variance of returns calculation
def port_mean_var(W, R, C):
    return port_mean(W, R), port_var(W, C)

# Given risk-free rate, assets returns and covariances, this function calculates
# mean-variance frontier and returns its [x,y] points in two arrays
def solve_frontier(R, C, rf):
    def fitness(W, R, C, r):
        # For given level of return r, find weights which minimizes portfolio variance.
        mean, var = port_mean_var(W, R, C)
        penalty = 100 * abs(mean - r) # Big penalty for not meeting stated portfolio return effectively serves as optimization constraint
        return var + penalty

    frontier_mean, frontier_var = [], []
    n = len(R)  # Number of assets in the portfolio
    for r in np.linspace(min(R), max(R), num=20):  # Iterate through the range of returns on Y axis
        W = np.ones([n]) / n  # start optimization with equal weights
        b_ = [(0., 1.) for i in range(n)]
        c_ = ({'type': 'eq', 'fun': lambda W: sum(W) - 1.})
        optimized = scipy.optimize.minimize(fitness, W, (R, C, r), method='SLSQP', constraints=c_, bounds=b_)
        if not optimized.success:
            raise BaseException(optimized.message)
        # add point to the efficient frontier [x,y] = [optimized.x, r]
        frontier_mean.append(r)
        frontier_var.append(port_var(optimized.x, C))
    return array(frontier_mean), array(frontier_var)

# Given risk-free rate, assets returns and covariances, this function calculates
# weights of tangency portfolio with respect to sharpe ratio maximization
def solve_weights(R, C, rf):
    def fitness(W, R, C, rf):
        mean, var = port_mean_var(W, R, C)  # calculate mean/variance of the portfolio
        util = (mean - rf) / np.sqrt(var)  # utility = Sharpe ratio
        return 1 / util  # maximize the utility, minimize its inverse value
    n = len(R)
    W = np.ones([n]) / n  # start optimization with equal weights
    b_ = [(0., 1.) for i in range(n)]  # weights for boundaries between 0%..100%. No leverage, no shorting
    c_ = ({'type': 'eq', 'fun': lambda W: sum(W) - 1.})  # Sum of weights must be 100%
    optimized = scipy.optimize.minimize(fitness, W, (R, C, rf), method='SLSQP', constraints=c_, bounds=b_)
    if not optimized.success: raise BaseException(optimized.message)
    return optimized.x

class Result:
    def __init__(self, W, tan_mean, tan_var, front_mean, front_var):
        self.W = W
        self.tan_mean = tan_mean
        self.tan_var = tan_var
        self.front_mean = front_mean
        self.front_var = front_var

def optimize_frontier(R, C, rf):
    W = solve_weights(R, C, rf)
    tan_mean, tan_var = port_mean_var(W, R, C)  # calculate tangency portfolio
    front_mean, front_var = solve_frontier(R, C, rf)  # calculate efficient frontier
    # Weights, Tangency portfolio asset means and variances, Efficient frontier means and variances
    return Result(W, tan_mean, tan_var, front_mean, front_var)

def display_assets(names, R, C, color='black'):
    n = len(names)
    plt.scatter([C[i, i] ** .5 for i in range(n)], R, marker='x', color=color), plt.grid(True)  # draw assets
    for i in range(n):
        plt.text(C[i, i] ** .5, R[i], '  %s' % names[i], verticalalignment='center', color=color) # draw labels

def display_frontier(result, label=None, color='black'):
    plt.text(result.tan_var ** .5, result.tan_mean, '   tangent', verticalalignment='center', color=color)
    plt.scatter(result.tan_var ** .5, result.tan_mean, marker='o', color=color), plt.grid(True)
    plt.plot(result.front_var ** .5, result.front_mean, label=label, color=color), plt.grid(True)  # draw efficient frontier

# Function loads historical stock prices of nine major S&P companies and returns them together
# with their market capitalizations, as of 2013-07-01
def load_data(caps):
    n = len(caps)
    prices_out, caps_out = [], []
    for s in caps:
        dataframe = pandas.read_csv('../DATA/CSV/%s.csv' % s, index_col=None, parse_dates=['date'])
        prices = list(dataframe['close'])[-500:] # trailing window 500 days
        prices_out.append(prices)
        caps_out.append(caps[s])
    return list(caps.keys()), prices_out, caps_out

# Function takes historical stock prices together with market capitalizations and
# calculates weights, historical returns and historical covariances
def assets_historical_returns_and_covariances(prices):
    prices = np.matrix(prices)  # create numpy matrix from prices
    # create matrix of historical returns
    rows, cols = prices.shape
    returns = np.empty([rows, cols - 1])
    for r in range(rows):
        for c in range(cols - 1):
            p0, p1 = prices[r, c], prices[r, c + 1]
            returns[r, c] = (p1 / p0) - 1
    # calculate returns
    expreturns = array([])
    for r in range(rows):
        expreturns = np.append(expreturns, np.mean(returns[r]))
    # calculate covariances
    covars = np.cov(returns)
    expreturns = (1 + expreturns) ** 250 - 1  # Annualize returns
    covars = covars * 250  # Annualize covariances
    return expreturns, covars

def create_views_and_link_matrix(names, views):
    r, c = len(views), len(names)
    Q = [views[i][3] for i in range(r)]  # view matrix
    P = np.zeros([r, c])
    nameToIndex = dict()
    for i, n in enumerate(names):
        nameToIndex[n] = i
    for i, v in enumerate(views):
        name1, name2 = views[i][0], views[i][2]
        P[i, nameToIndex[name1]] = +1 if views[i][1] == '>' else -1
        P[i, nameToIndex[name2]] = -1 if views[i][1] == '>' else +1
    return array(Q), P


if __name__ == '__main__':

    # 자산배분할 자산들의 리스트 및 시가총액을 설정
    capitalizations = {'XOM': 403.02e9, 'AAPL': 392.90e9, 'MSFT': 283.60e9, 'JNJ': 243.17e9, 'GE': 236.79e9, 'GOOG': 292.72e9, 'CVX': 231.03e9, 'PG': 214.99e9, 'WFC': 218.79e9}
    names, prices, caps = load_data(capitalizations)

    # 자산별 기본 데이터 설정 및 생성
    W = array(caps) / sum(caps) # calculate market weights from capitalizations
    R, C = assets_historical_returns_and_covariances(prices)
    rf = .015  # Risk-free rate

    #print(pandas.DataFrame({'Return': R, 'Weight (based on market cap)': W}, index=names).T)
    #print(pandas.DataFrame(C, columns=names, index=names))

    DRAW_FIGURE = True

    MEAN_VARIANCE_OPTIMIZATION = True
    if MEAN_VARIANCE_OPTIMIZATION:
        res1 = optimize_frontier(R, C, rf)

        if DRAW_FIGURE:
            display_assets(names, R, C, color='blue')
            display_frontier(res1, color='blue')
            plt.xlabel('variance $\sigma$'), plt.ylabel('mean $\mu$'), plt.show()
        print(pandas.DataFrame({'Weight': res1.W}, index=names).T)

    BLACK_LITTERMAN_MODEL = True
    if BLACK_LITTERMAN_MODEL:
        # Calculate portfolio historical return and variance
        mean, var = port_mean_var(W, R, C)

        lmb = (mean - rf) / var  # Calculate risk aversion
        Pi = np.dot(np.dot(lmb, C), W)  # Calculate equilibrium excess returns

        res2 = optimize_frontier(Pi + rf, C, rf)

        if DRAW_FIGURE:
            if MEAN_VARIANCE_OPTIMIZATION:
                display_assets(names, R, C, color='red')
                display_frontier(res1, label='Historical returns', color='red')
            display_assets(names, Pi + rf, C, color='green')
            display_frontier(res2, label='Implied returns', color='green')
            plt.xlabel('variance $\sigma$'), plt.ylabel('mean $\mu$'), plt.legend(), plt.show()
        print(pandas.DataFrame({'Weight': res2.W}, index=names).T)

        VIEW_ADJUSTED = True
        if VIEW_ADJUSTED:
            # 자산별 전망 설정
            views = [(names[0], '>', names[3], 0.02),
                     (names[1], '<', names[5], 0.02),
                     (names[2], '<', names[4], 0.03)]
            Q, P = create_views_and_link_matrix(names, views)
            #print('Views Matrix')
            #print(DataFrame({'Views':Q}))
            #print('Link Matrix')
            #print(DataFrame(P))

            # tau를 바꾸는게 무슨 의미가 있는지 모르겠음.(수식을 전개하면 tau는 사라진다.)
            #for tau in np.linspace(.01, 0.1, num=100):
            tau = .025  # scaling factor
            # Calculate omega - uncertainty matrix about views
            omega = np.dot(np.dot(tau*P, C), np.transpose(P))  # 0.025 * P * C * transpose(P)
            # Calculate equilibrium excess returns with views incorporated
            sub_a = np.linalg.inv(tau*C)
            sub_b = np.dot(np.dot(np.transpose(P), np.linalg.inv(omega)), P)
            sub_c = np.dot(np.linalg.inv(tau*C), Pi)
            sub_d = np.dot(np.dot(np.transpose(P), np.linalg.inv(omega)), Q)
            Pi_adj = np.dot(np.linalg.inv(sub_a + sub_b), (sub_c + sub_d))

            res3 = optimize_frontier(Pi_adj + rf, C, rf)

            if DRAW_FIGURE:
                if MEAN_VARIANCE_OPTIMIZATION:
                    display_assets(names, R, C, color='red')
                    display_frontier(res1, label='Historical returns', color='red')
                display_assets(names, Pi + rf, C, color='green')
                display_frontier(res2, label='Implied returns', color='green')
                display_assets(names, Pi_adj + rf, C, color='blue')
                display_frontier(res3, label='Implied returns (adjusted views)', color='blue')
                plt.xlabel('variance $\sigma$'), plt.ylabel('mean $\mu$'), plt.legend(), plt.show()
            print(pandas.DataFrame({'Weight': res3.W}, index=names).T)