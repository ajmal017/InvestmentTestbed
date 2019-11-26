# Portfolio 최적화의 지도학습을 위해 label 데이터를 생성한다.
# train data와 label을 이용하여 지도학습을 수행한다.
#
# 2019.11.11 아마추어 퀀트 (blog.naver.com/chunjein)
# --------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import Model
from keras.layers import Input, Dense, LSTM
from keras.optimizers import Adam
import pickle

ALPHA =  0.0005
nLstmTimeStep = 40
nLstmHidden = 32
nFcHidden = 32

saver = "data/4.weights.h5"
trainData = "data/3.trainData.pickle"
resultW = "data/5.result.csv"

# 저장된 학습 데이터를 읽어온다.
with open(trainData, 'rb') as f:
    [trainD, label, todayD] = pickle.load(f)

nLstmTimeStep = trainD.shape[1]
nStock = trainD.shape[2]
        
# LSTM part
inputS = Input(batch_shape=(None, nLstmTimeStep, nStock))
lstmOut = LSTM(nLstmHidden)(inputS)

# Feed forward part
fcOut = Dense(nFcHidden, activation='relu')(lstmOut)
prob = Dense(nStock, activation='softmax')(fcOut)

nw = Model(inputs=[inputS], outputs=[prob])
nw.compile(optimizer=Adam(lr=ALPHA), loss='categorical_crossentropy')

# 기존 학습 결과가 있으면, 이를 적용하고, 없으면 랜덤 값에서 시작한다.
try:
    nw.load_weights(saver)
    print("\n# 기존 학습 결과 Weight를 적용하였습니다.")
except:
    print("\n# Actor/Critic Weight을 랜덤 초기화 하였습니다.")
              
# LSTM을 학습한다.
nw.fit(trainD, label, batch_size=100, epochs=1000, shuffle=True)

# 오늘의 최적 비중을 확인해 본다.
prob = nw.predict(todayD)[0]
plt.bar(np.arange(len(prob)), prob)
plt.show()
print(prob)
    
# 학습 결과 Weight를 저장해 둔다
nw.save_weights(saver)

def recallLSTM():
    for i, D in enumerate(trainD):
        D = np.reshape(D, [1, nLstmTimeStep, nStock])
        prob = nw.predict(D)[0]
        
        if i == 0:
            w = prob
        else:
            w = np.vstack([w, prob])
        
        if i % 100 == 0:
            print("%d : 완료" % i)
            
    weights = pd.DataFrame(w)
    weights.to_csv(resultW, header=False, index=False)
