# Portfolio 최적화의 지도학습을 위해 label 데이터를 생성한다.
# label은 마코비츠의 포트폴리오 비율을 적용한다.
#
# 2019.11.11 아마추어 퀀트 (blog.naver.com/chunjein)
# ---------------------------------------------------------
import numpy as np
import scipy.optimize as optimize
import matplotlib.pyplot as plt
import pickle
import numba as nb

# 저장된 학습 데이터를 읽어온다
with open('data/2.price_return.pickle', 'rb') as f:
    ds = pickle.load(f)
      
# 포트폴리오 최적화를 위한 목표함수. Sharp Ratio를 최대화한다.
@nb.njit
def sharpRatio(w, *args):
    rtn = args[0]
    cm = args[1]
    reg = args[2]

    # 포트폴리오의 연간 수익률
    portRtn = np.dot(w, rtn) * 252
    
    # 포트폴리오의 연간 변동성
    portVol = np.sqrt(np.dot(w, np.dot(cm, w.T))) * np.sqrt(252)
    
    # Sharp ratio를 계산한다. minimize를 위해 음수를 붙임.
    sr = -portRtn / portVol + reg * np.sum(w ** 2)
    return sr

# 제한 조건. Weight의 총합 = 1.0
@nb.njit
def constraint1(w):
    return np.sum(w) - 1.0

# 포트폴리오를 최적화한다.
# reg : Regularization constant
def optPortfolio(rv, W0, reg=100):
    R = np.mean(rv, axis=0)                 # 종목 별 평균 수익률
    C = np.cov(rv.T)                        # 종목 별 수익률의 공분산 행렬
    
    # 최적 포트폴리오의 비율 (W)을 계산한다
    bnds = ((0., 1.0),) * len(W0)
    cons = {'type' : 'eq', 'fun' : constraint1}
    p = optimize.minimize(fun=sharpRatio, x0=W0, args=(R, C, reg), method='SLSQP', bounds=bnds, constraints=cons)
    
    return p.x, p.success

# 마코비츠의 포트폴리오 최적화 결과 label을 생성한다.
def labeling():
    # 종목 별 초기 weight : 균등분포
    W0 = np.ones(len(ds[0][0])) / len(ds[0][0])
    
    nErr = 0
    regC = 30   # regularization constant = 50 적용 (overfitting 방지용)
    for i in range(1, len(ds)):     # 1부터 시작함. label은 미래의 값으로 설정함.
        w, success = optPortfolio(ds[i], W0, regC)
        
        if not success:
            print("%d 행 데이터에서 수렴하지 못했습니다." % i)
            nErr += 1
        
        if i < 2:
            label = w
        else:
            label = np.vstack([label, w])
        
        if i % 100 == 0:
            print("%d : 완료" % i)
        
        # 다음 루프의 초기 weight는 이전의 최적 w를 적용한다.
        W0 = w
    
    print("label 데이터를 생성했습니다. 에러 개수 = %d" % nErr)
    return label

# 임의 label에 대한 bar plot을 육안으로 확인해 본다
# showLabel(label[0]) <-- 첫째 날 종목 별 w 관찰
def showLabel(y):
    plt.bar(np.arange(len(y)), y)
    plt.show()
    print(y)

# 임의 종목에 대한 비중 (w) 변화를 육안으로 확인해 본다
# traceLabel(label, 0) <-- 첫 번째 종목의 w 변화 관찰
def traceLabel(y, n):
    plt.figure(figsize=(10,6))
    plt.plot(y[:, n])
    plt.show()

# label을 생성한다.
# label은 포트폴리오에 들어가는 종목들의 Sharp Ratio를 최대화하는 Weight를 의미한다.
label = labeling()

# label을 저장해 둔다.
trainD = ds[0:-1]
todayD = ds[-1:]
with open('data/3.trainData.pickle', 'wb') as f:
    pickle.dump([trainD, label, todayD], f, pickle.HIGHEST_PROTOCOL)

# Dataset을 로드하고, 확인해 본다.
with open('data/3.trainData.pickle', 'rb') as f:
    [trainD, label, todayD] = pickle.load(f)


