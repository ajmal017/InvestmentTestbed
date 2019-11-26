# N-step TD LSTM-Actor-Critic 실습 : Portfolio 최적화. max(Return)
#
# 2019.11.11 아마추어 퀀트 (blog.naver.com/chunjein)
# ------------------------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import Model
from keras.layers import Input, Dense, LSTM
from keras.optimizers import Adam
from keras import backend as K
import pickle

ALPHA =  0.0005
GAMMA = 0.99
MAX_ENTROPY = 0.001
INC_WEIGHT = 0.2
nStock = 11
nAction = nStock
nHidden = 16
nActOut = nAction
nStepTD = 3
nLstmTimeStep = 20
nLstmHidden = 32

actor_saver = "data/2.actor_weights.h5"
critic_saver = "data/2.critic_weights.h5"
trainData = "data/1.trainData.pickle"
verifyData = "data/1.trainData.csv"

# LSTM-Actor-Critic Network을 생성한다.
def BuildActorCritic():
    # LSTM은 actor와 critic이 공유한다.
    inputS = Input(batch_shape=(None, nLstmTimeStep, nStock))
    state = LSTM(nLstmHidden)(inputS)
    
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
    state = np.reshape(state, [1, nLstmTimeStep, nStock])
    delta = np.reshape(delta, (1, 1))
    action = np.reshape(action, (1, nAction))
    return model.fit([state, delta], action, epochs=1, verbose=False)

# Critic을 학습한다.
def learnCritic(model, state, target):
    state = np.reshape(state, [1, nLstmTimeStep, nStock])
    target = np.reshape(target, (1, 1))
    return model.fit(state, target, epochs=1, verbose=False)

# Actor와 Critic의 결과를 인출한다.
def recall(model, state):
    state = np.reshape(state, [1, nLstmTimeStep, nStock])
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
    p = recall(model, state)
    
    # 데이터 타입 때문에 multinomial()에서 sum(pvals[:-1]) > 1.0 에러가 발생하는 경우가 있음.
    p = np.asarray(p).astype('float64')
    p = p / np.sum(p)
    
    act = np.random.multinomial(1, p) * 1.0
    action = np.zeros(nAction)
    action[myArgmax(act)] = 1.0

    return action

# 학습
def Training(actor, policy, critic, data):
    rewardTraj = [0.0]
    
    # 매일 매일 거래하지 않고 일정기간을 건너뛰면서 거래한다.
    start = int(np.random.rand() * 100) + 1
    step = int(np.random.normal(20, 5)) + 1      # 평균 10일 표준편차 5일
    step = np.max([1, step])
    
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
            # 현재 상태의 portfolio value.
            # Rebalancing 없이 현재 비중을 유지한다면, 향후 currPV 만큼 변화할 것임.
            currPV = np.dot(data[i+step][-1], np.array(tradeWeight).T)
            
            # 선택한 종목의 비중을 늘림. 이 만큼 Rebalancing을 수행하면 향후 nextPV 만큼 변화할 것임.
            tradeWeight[np.argmax(currAction)] += INC_WEIGHT
            tradeWeight = mySoftmax(tradeWeight)
            nextPV = np.dot(data[i+step][-1], np.array(tradeWeight).T)
            
            # reward = rebalancing 수행으로 인해 변화된 portfolio value로 정의함
            reward = nextPV - currPV
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
        Training(actor, policy, critic, fs)        
        print("%d) 학습 완료" % (i+1))
    
    # 학습 결과 Weight를 저장해 둔다
    actor.save_weights(actor_saver)
    critic.save_weights(critic_saver)

def verify():
    K.clear_session()
    actor, policy, critic = BuildActorCritic()
    
    try:
        actor.load_weights(actor_saver)
        critic.load_weights(critic_saver)
        print("\n# 기존 학습 결과 Weight를 적용하였습니다.")
    except:
        print("\n# Actor/Critic Weight을 랜덤 초기화 하였습니다.")
              
    # 저장된 학습 데이터를 읽어온다
    ds = pd.read_csv(verifyData)
    with open(trainData, 'rb') as f:
        fs = pickle.load(f)
        
    for x in fs:
        w = recall(policy, x)
        print(np.round(w,3))
        
    plt.bar(np.arange(11), w)
    plt.show()
