# 최적 포트폴리오의 성과를 육안으로 확인한다.
# 거래 비용은 고려하지 않았음.
#
# 2019.11.11 아마추어 퀀트 (blog.naver.com/chunjein)
# --------------------------------------------------------
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

# 종목 별 수익률에 투자 비율을 적용해서 포트폴리오 가치를 계산한다.
def portfolioValue(rtnX, w):
    # 데이터 프레임을 배열로 변환한다
    x = np.array(rtnX)
    y = np.array(w)
    
    # 수익률 * weight를 계산한 후 결과를 데이터 프레임으로 변환한다.
    v = np.sum(x * y, axis = 1)
    v = pd.DataFrame(v)
    v.index = rtnX.index
    v.columns = ['Rp']
    
    # S의 누적 relative price를 계산한다.
    v['Rel_prc'] = np.exp(v['Rp'])
    v['Sp'] = pd.DataFrame(v['Rel_prc']).cumprod()
    return v

# 종목 별 w 변화와 누적 relative price 차트를 관찰한다.
def showPV(rtnX, w):
    # 종목 별 w 변화를 관찰한다.
    plt.figure(figsize=(12,8))
    plt.plot(np.array(w), linewidth=1)
    plt.title("Portfolio Weights", fontsize=14)
    leg = plt.legend(list(rtnX.columns), prop={'size': 12})
    for i in leg.legendHandles:
        i.set_linewidth(5)
    plt.show()
    
    # w를 적용해서 portfolio value를 계산한다.
    pv = portfolioValue(rtnX, w)
    
    # portfolio의 최종 (이산) 수익률을 계산한다.
    Rp = 100.0 * (pv['Sp'][-1] - pv['Sp'][0]) / pv['Sp'][0]
    
    # 누적 수익률 차트를 그린다.
    plt.figure(figsize=(12,8))
    plt.plot(np.array(pv['Sp']), linewidth=1)
    plt.title("Portfolio Value (Relative price)", fontsize=14)
    plt.show()
    
    print("* 포트폴리오 수익률 = %.2f (%s), 연간 %.2f (%s)" % (Rp, '%', Rp * 252.0 / len(pv), '%'))

# LSTM으로 찾은 데이터 (result.csv)를 읽어온다.
rtnX = pd.read_csv('data/1.price_return.csv', index_col='date')[39:]
w = pd.read_csv('data/2-3.result.csv', header=None)
w.index = rtnX.index

# w를 적용한 portfolio value의 변화를 관찰한다.
showPV(rtnX, w)

# pctX를 적용한 오늘의 최적 포트폴리오 비율을 표시한다.
df = pd.DataFrame(np.array(w[-1:] * 100).T)
df.columns = ['W']
df['stock'] = list(rtnX.columns)

ax = df.plot(x='stock', y='W', kind='bar', legend=False, width=0.8, figsize=(8,6), fontsize=12) 
x_offset = -0.4
y_offset = 0.2
for p in ax.patches:
    b = p.get_bbox()
    val = "{:.2f}{}".format(b.y1 + b.y0, '%')
    ax.annotate(val, ((b.x0 + b.x1)/2 + x_offset, b.y1 + y_offset), fontsize=12, color='red')
plt.title("Today's optimal portfolio weights", fontsize=14)
plt.show()
