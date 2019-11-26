# N-step TD LSTM-Actor-Critic 실습 : Portfolio 최적화. max(Sharp Ratio)
#
# 2019.11.11 아마추어 퀀트 (blog.naver.com/chunjein)
# ------------------------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import Model
from keras.layers import Input, Dense, Conv2D, Flatten
from keras.optimizers import Adam
from keras import backend as K
import pickle

ALPHA =  0.0005
GAMMA = 0.95
MAX_ENTROPY = 0.03
INC_WEIGHT = 0.1
nStock = 11
nAction = nStock
nHidden = 16
nActOut = nAction
nStepTD = 1
nLstmTimeStep = 40

trainData = "data/2.price_return.pickle"
actor_saver = "data/3-1.actor_weights.h5"
critic_saver = "data/3-2.critic_weights.h5"
resultW = "data/3-3.result.csv"

# LSTM-Actor-Critic Network을 생성한다.
def BuildActorCritic():
    # LSTM은 actor와 critic이 공유한다.
    inputS = Input(batch_shape=(None, nLstmTimeStep, nStock, 1))
    xConv = Conv2D(filters = 16, kernel_size=(10, 5), activation='relu')(inputS)
    state = Flatten()(xConv)
    
    # Actor
    delta = Input(shape = [1])
    actorH = Dense(nHidden, activation='relu')(state)
    prob = Dense(nAction, activation='softmax')(actorH)

    def actorLoss(trueY, predY):
        clipY = K.clip(predY, 1e-8, 1-1e-8)
        ce = -delta * trueY * K.log(clipY) + MAX_ENTROPY * clipY * K.log(clipY)
        return K.sum(ce)
    
    actor = Model(inputs=[inputS, delta], outputs=[prob])
    actor.compile(optimizer=Adam(lr=ALPHA), loss=actorLoss)
    policy = Model(inputs=[inputS], outputs=[prob])
    
    # Critic
    cirticH = Dense(nHidden, activation='relu')(state)
    value = Dense(1, activation='linear')(cirticH)
    critic = Model(inputs=[inputS], outputs=[value])
    critic.compile(optimizer=Adam(lr=ALPHA), loss='mean_squared_error')
    
    return actor, policy, critic

# Actor를 학습한다.
def learnActor(model, state, delta, action):
    state = np.reshape(state, [1, nLstmTimeStep, nStock, 1])
    delta = np.reshape(delta, (1, 1))
    action = np.reshape(action, (1, nAction))
    return model.fit([state, delta], action, epochs=1, verbose=False)

# Critic을 학습한다.
def learnCritic(model, state, target):
    state = np.reshape(state, [1, nLstmTimeStep, nStock, 1])
    target = np.reshape(target, (1, 1))
    return model.fit(state, target, epochs=1, verbose=False)

# Actor와 Critic의 결과를 인출한다.
def recall(model, state):
    state = np.reshape(state, [1, nLstmTimeStep, nStock, 1])
    return model.predict(state)[0]

def myArgmax(d):
    maxValue = np.max(d)
    indices = np.where(np.asarray(d) == maxValue)[0]
    return np.random.choice(indices)

def mySoftmax(d):
    e = np.exp(d)
    return e / np.sum(e)

# 학습용 Action을 선택한다
def ChooseAction(model, state):
    # Actor로부터 주어진 상태 (state)에 대한 정책 (p)를 얻음.
    p = recall(model, state)
    
    # 데이터 타입 때문에 multinomial()에서 sum(pvals[:-1]) > 1.0 에러가 발생하는 경우가 있음.
    p = np.asarray(p).astype('float64')
    p = p / np.sum(p)
    
    action = np.zeros(nAction)
    if np.min(p) <= 0.01:
        # p = [1, 0, 0] 처럼 sparse한 형태이면 이후로는 exploration이 일어나지 않음.
        # exploration을 위해 확률이 0에 가까운 것을 선택함. 한번만 선택해 주면 
        # MAX_ENTROPY의해 sparse한 현상이 잘 발생하지 않을 것임.
        action[np.argmin(p)] = 1.0
    else:
        act = np.random.multinomial(1, p) * 1.0
        action[myArgmax(act)] = 1.0

    return action

# 학습
def Training(actor, policy, critic, data):
    rewardTraj = [0.0]
    
    # 매일 매일 거래하지 않고 일정 기간을 건너뛰면서 거래한다.
    start = int(np.random.rand() * 100) + 1
    step = int(np.random.normal(20, 5)) + 1      # 평균 10일 표준편차 5일
    step = np.max([1, step])
    step = 10
    # 초기 상태를 설정한다.
    currState = data[start]
    stateTraj = [currState]
    
    # 초기 action을 선택한다. 한 종목을 선택한다.
    currAction = ChooseAction(policy, currState)
    actionTraj = [currAction]
    
    T = float('inf')
    t = 0
    tau = 0
    for i in range(start, len(data) - step, step):
        # current state가 terminal 상태인지 판단한다.
        # i --> current state, (i + step) --> next state
        if i >= len(data) - step:
            terminal = True
        else:
            terminal = False
        
        # 현재 상태의 투자 비중을 읽어온다.
        tradeWeight = recall(policy, currState)
        
        if t < T:
            # currAction을 실행하고, reward, nextState 측정한다.
            # 선택한 종목의 비중을 늘림. 이 만큼 Rebalancing을 수행하면 향후 reward 만큼 변화할 것임.
            tradeWeight[np.argmax(currAction)] += INC_WEIGHT
            tradeWeight = mySoftmax(tradeWeight)
            C = np.cov(data[i+step].T)
            meanRtn = np.dot(np.mean(data[i+step], axis=0), tradeWeight.T) * 252
            meanStd = np.sqrt(np.dot(np.dot(tradeWeight.T, C), tradeWeight) * 252)
            reward = meanRtn / meanStd  # sharp ratio
            rewardTraj.append(reward)
    
            # next state
            nextState = data[i + step]
            stateTraj.append(nextState)
            
            if terminal:
                T = t + 1
            else:
                nextAction = ChooseAction(policy, nextState)
                actionTraj.append(nextAction)
            
        tau = t - nStepTD + 1
        if tau >= 0:
            target = 0.0
            for k in range(tau + 1, int(np.min([tau + nStepTD, T])) + 1):
                target += pow(GAMMA, k-tau-1) * rewardTraj[k]
            
            if tau + nStepTD < T:
                lastState = stateTraj[tau + nStepTD]
                target += pow(GAMMA, nStepTD) * recall(critic, lastState)

            # 업데이트 할 state, action
            updateState = stateTraj[tau]
            updateAction = actionTraj[tau]
            
            # Critic을 학습한다.
            learnCritic(critic, updateState, target)
    
            # Actor를 학습한다.
            delta = target - recall(critic, updateState)
            learnActor(actor, updateState, delta, updateAction)

        if terminal:
            break
        else:
            currState = nextState
            currAction = nextAction
            
        t += 1
        
    # 육안 확인을 위해 마지막 상태의 critic value를 리턴한다.
    return recall(critic, stateTraj[-1])

# 학습을 시작한다
def learn(n):
    K.clear_session()
    actor, policy, critic = BuildActorCritic()
    
    try:
        actor.load_weights(actor_saver)
        critic.load_weights(critic_saver)
        print("\n# 기존 학습 결과 Weight를 적용하였습니다.")
    except:
        print("\n# Actor/Critic Weight을 랜덤 초기화 하였습니다.")
    
    # 저장된 학습 데이터를 읽어와서 학습한다.
    with open(trainData, 'rb') as f:
        fs = pickle.load(f)
        
    for i in range(0, n):
        value = Training(actor, policy, critic, fs)        
        print("%d) critic value = %.4f" % (i+1, value))
    
    # 학습 결과 Weight를 저장해 둔다
    actor.save_weights(actor_saver)
    critic.save_weights(critic_saver)

def recallAAC():
    K.clear_session()
    actor, policy, critic = BuildActorCritic()
    
    try:
        actor.load_weights(actor_saver)
        critic.load_weights(critic_saver)
        print("\n# 기존 학습 결과 Weight를 적용하였습니다.")
    except:
        print("\n# Actor/Critic Weight을 랜덤 초기화 하였습니다.")
              
    # 저장된 학습 데이터를 읽어온다
    with open(trainData, 'rb') as f:
        ds = pickle.load(f)
    
    for i, x in enumerate(ds):
        prob = recall(policy, x)
    
        if i == 0:
            w = prob
        else:
            w = np.vstack([w, prob])
        
        if i % 100 == 0:
            print("%d : 완료" % i)
            
    weights = pd.DataFrame(w)
    weights.to_csv(resultW, header=False, index=False)
    
def tradeWeight():
    K.clear_session()
    actor, policy, critic = BuildActorCritic()
    
    try:
        actor.load_weights(actor_saver)
        critic.load_weights(critic_saver)
        print("\n# 기존 학습 결과 Weight를 적용하였습니다.")
    except:
        print("\n# Actor/Critic Weight을 랜덤 초기화 하였습니다.")
              
    # 저장된 학습 데이터를 읽어온다
    with open(trainData, 'rb') as f:
        fs = pickle.load(f)
    
    vTraj = []
    tradeWeight = np.array([1/nStock] * nStock)  # 첫 날은 균등분포에서 시작함.
    for i, x in enumerate(fs):
        # critic value 확인을 위해 저장해 둔다.
        v = recall(critic, x)
        vTraj.append(v)
        
        # 마지막 날은 제외함. tradeWeight * next day's return으로 성능 시험을 해야 함.
        # 첫째 날은 tradeWeight가 균등분포이고, 첫째 날로 recall한 tradeWeight는 둘째 날
        # 위치에 기록함. 마지막 recall은 그 다음날 수익률이 없으므로 제외함.
        if i < len(fs) - 1:
            tradeWeight = np.vstack((tradeWeight, recall(policy, x)))
            
    # 학습데이터에 tradeWeight를 합친다.
    ds = pd.read_csv(verifyData)[39:]
    w = pd.DataFrame(tradeWeight, index=ds['date'])
    w.columns = ['w' + str(x+1) for x in np.arange(11)]
    result = pd.merge(ds, w, on='date', how='right')
    result = result.set_index('date')
    
    return result, np.array(vTraj), recall(policy, fs[-1])
    
def portfolioValue(df, randomW = False, softBeta = 2.0):
    pv = []
    for idx, r in df.iterrows():
        x = np.array(r[:11])
        
        if randomW:
            rw = np.random.random(11)
            e = np.exp(rw / softBeta)
            w = e / np.sum(e)
        else:
            w = np.array(r[11:])
        pv.append(np.dot(x, w.T))
    
    S0 = 1
    S = [1.0]
    for rtn in pv:
        S.append(S0 * np.exp(rtn))
        S0 = S[-1]
        
    plt.figure(figsize=(12, 8))
    plt.plot(S)
    plt.title("Portfolio Value")
    plt.show()

def plotCriticValue(v, start=0):
    plt.figure(figsize=(12, 8))
    plt.plot(v[start:])
    plt.title("Critic Value")
    plt.show()

def verify(stock = 'w1'):
    df, value, w = tradeWeight()
    portfolioValue(df)
    plotCriticValue(value)
    
    # 마지막 날의 optimal weights를 관찰한다.
    plt.figure(figsize=(12, 8))
    plt.bar(np.arange(11), w)
    plt.title("Today's optimal weights")
    plt.show()
    
    # n-번째 종목의 weight 변화를 관찰한다.
    plt.figure(figsize=(12, 8))
    plt.plot(np.array(df[stock]))
    plt.title(stock + " weights")
    plt.show()
    