# encoding: utf-8
"""
@author:  lingxiao he
@contact: xiaomingzhidao1@gmail.com
"""

import numpy as np


def sma(data, window):
    """
    计算简单移动平均线（SMA）。

    参数：
    data: List[float]，待计算的数据序列。
    window: int，移动窗口的大小。

    返回：
    List[float]，SMA序列。
    """
    sma_values = []
    for i in range(len(data)):
        if i < window:
            sma_values.append(sum(data[:i+1])/len(data[:i+1]))
        else:
            sma_values.append(sum(data[i-window+1:i+1])/window)
    return sma_values

def ema(data, window):
    """
    计算指数平滑移动平均线（EMA）。

    参数：
    data: List[float]，待计算的数据序列。
    window: int，移动窗口的大小。

    返回：
    List[float]，EMA序列。
    """
    ema_values = []
    alpha = 2/(window+1)
    ema_values.append(data[0])
    for i in range(1, len(data)):
        ema_values.append(alpha*data[i] + (1-alpha)*ema_values[-1])
    return ema_values
 
def smma(data, period):
    """
    计算平滑移动平均线（SMMA）。

    参数：
    data: List[float]，待计算的数据序列。
    window: int，移动窗口的大小。

    返回：
    List[float]，EMA序列。
    """
    smma_values = []
    prev_smma = sum(data[:period]) / period
    smma_values.append(prev_smma)
    for i in range(period, len(data)):
        smma = (prev_smma * (period - 1) + data[i]) / period
        smma_values.append(smma)
        prev_smma = smma
    return smma_values


def calc_zlema(src, length):
    ema1 = ema(src, length)
    ema2 = ema(ema1, length)
    d = np.array(ema1) - np.array(ema2)
    return np.array(ema1) + d


def MACD(price, fast_period=12, slow_period=26, signal_period=9):
    """
    计算移动平均线(MACD)和信号线(Signal line)
    
    参数：
    price：收盘价的时间序列数据
    fast_period：快速移动平均线的时间周期，默认为12
    slow_period：慢速移动平均线的时间周期，默认为26
    signal_period：信号线的时间周期，默认为9
    
    返回值：
    包含MACD和Signal line的DataFrame对象
    """
    # 计算快速移动平均线
    fast_ema = ema(price, fast_period)
    
    # 计算慢速移动平均线
    slow_ema = ema(price, slow_period)
    
    # 计算DIF
    DIF = np.array(fast_ema) - np.array(slow_ema)
    
    # 计算DEA
    DEA = np.array(ema(DIF, signal_period))
    # 计算MACD
    MACD = DIF - DEA
    
    
    return MACD, DIF, DEA

def Impulse_MACD(prices, lengthMA=34, lengthSignal=9):
    """
    计算脉冲移动平均线(Impluse MACD)
    
    参数：
    prices：收盘价、最高价、最低价的时间序列数据
    lengthMA：K线的时间周期，默认为34
    lenhthSignal：信号线的时间周期，默认为9
    
    返回值：
    包含MACD和Signal line的DataFrame对象
    """
    src = (prices[0] + prices[1] + prices[2])/3
    
    hi = np.array(smma(prices[1], lengthMA))
    lo = np.array(smma(prices[2], lengthMA))
    mi = calc_zlema(src, lengthMA)
    mi = mi[len(mi)-len(hi):]
    md = np.zeros_like(mi) 
    for i in range(len(md)):
        if mi[i] > hi[i]:
            md[i] = mi[i] - hi[i]
        elif mi[i] < lo[i]:
            md[i] = mi[i] - lo[i]
        else:
            md[i] = 0

    sb = sma(md, lengthSignal)
    red_line = md
    yellow_line = sb
    sh = md-sb
    return red_line, yellow_line, sh


