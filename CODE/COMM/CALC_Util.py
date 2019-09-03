#_*_ coding: utf-8 _*_

import sys

def getEconomicDiff(value, prev_value, unit):
    diff = 0
    try:
        if unit == 'p':
            diff = value - prev_value
        elif unit == 'n':
            if prev_value >= 0:
                diff = value/prev_value-1
            # 기준이 되는 이전 값이 음수인 경우 -를 곱함 
            elif prev_value < 0:
                diff = -(value/prev_value-1)
    # 기준이 되는 이전 값이 0인 경우는 무시함
    except (ZeroDivisionError) as e:
        #print('에러정보 : ', e, file=sys.stderr)
        diff = None

    return diff