# Portfolio 최적화를 위한 데이터를 생성한다.
# 종목별 일일 주가 데이터로부터 수익률을 계산하고 LSTM 입력용 수익률 sequence 데이터를 생성한다.
#
# 교육자료 : Reinforcement Learning for Finance
# 2019.11.11 아마추어 퀀트 (blog.naver.com/chunjein)
# ---------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import pickle

PRC_RETURN = 0  # 수익률
PRC_RATIO = 1   # 가격 비율

nTimeStep = 40
nStock = 11
stockList = ['005930','000660','005490','035420','017670','055550','105560','066570','006800','009150','015760']
stockDataDir = './stockData/'

# 종목별 수익률 계산
def makeReturnData(pType = PRC_RETURN):
    for i, s in enumerate(stockList):
        sCode = stockDataDir + s + '.csv'
        
        # sCode 종목의 종가 데이터를 읽어온다.
        prc = pd.read_csv(sCode, index_col = [0], parse_dates=True)
        closePrc = pd.DataFrame(prc.loc[:, 'close'].sort_index())
        
        if pType == PRC_RETURN:
            # 종가 기준으로 수익률을 계산한다.
            rtn = pd.DataFrame(np.log(closePrc['close']) - np.log(closePrc['close'].shift(1)))
        else:
            # 종가 기준으로 전일 대비 가격 비율을 계산한다.
            rtn = pd.DataFrame(closePrc['close'] / closePrc['close'].shift(1))
        rtn.columns = ['a' + s]
        if i == 0:
            result = rtn
        else:
            result = pd.merge(result, rtn, on='date', how='right')
    
    return result.dropna()

# Feature sequence 데이터를 생성한다.
def makeFeatureSequence(data, step, n):
    seq = np.expand_dims(np.array(data.iloc[0:step, 0:n]), 0)
    
    for i in range(1, len(ds) - step + 1):
        x = np.expand_dims(np.array(data.iloc[i:(i+step), 0:n]), 0)
        seq = np.concatenate((seq, x))
    
    return seq

# 학습용 데이터 셋을 생성하고 저장한다.
ds = makeReturnData()
seqX = makeFeatureSequence(ds, nTimeStep, nStock)

ds.to_csv("data/1.trainData.csv")
with open('data/1.trainData2.pickle', 'wb') as f:
    pickle.dump(seqX, f, pickle.HIGHEST_PROTOCOL)
print("\n# 학습용 데이터를 생성했습니다.")

# Dataset을 로드하고, 확인해 본다.
with open('data/1.trainData.pickle', 'rb') as f:
    x = pickle.load(f)
      
