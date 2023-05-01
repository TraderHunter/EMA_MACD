# encoding: utf-8
"""
@author:  lingxiao he
@contact: xiaomingzhidao1@gmail.com
"""

import numpy as np
import pdb


def cal_ATR(prices, window, ratio):
    TR = prices[1] - prices[2]
    init_ATR = TR[:window].mean()
    ATR = []
    #pdb.set_trace()
    ATR.append(init_ATR)
    for i in range(window, len(TR)):
        ATR.append((ATR[i-window] * (window-1) + TR[i])/window)
    Chandelier_Exit = prices[1][-window:].max() - 2.5*ATR[-1]
    print(Chandelier_Exit)
    pdb.set_trace()

