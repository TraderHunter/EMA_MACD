#!/usr/bin/python
# -*- coding: UTF-8 -*-
import okex_api
import index
import pdb
import numpy as np
import schedule
import traceback
import time
import os
import random
import json
import csv

def coin_state(prices):
    EMA12 = index.ema(prices, 12)
    EMA25 = index.ema(prices, 25)
    EMA200 = index.ema(prices, 200)
    #pdb.set_trace()
    #prices[0]
    MACD, DIF, DEA = index.MACD(prices, 15, 34, 9)
    EMA12 = np.array(EMA12)
    EMA25 = np.array(EMA25)
    EMA200 = np.array(EMA200)
    MACD = np.array(MACD)
    

    return EMA12, EMA25, EMA200, MACD

def order_index(coinname, timetick):
    kline = okex_api.get_price(coinname, timetick, "1", 8)
    #pdb.set_trace()
    TradingVolume, prices = okex_api.kline_rank(kline)
    close_price = np.hstack([prices[0], float(okex_api.get_current_price(coinname)[0]['last'])])
    red_line, yellow_line, sh = index.Impulse_MACD(prices, lengthMA=34, lengthSignal=9)
    EMA12, EMA25, EMA200, MACD = coin_state(close_price)
    buyState = False
    sellState = False
    zs_price = 0
    if red_line[-2]<yellow_line[-2] and red_line[-1]>yellow_line[-1] and red_line[-1]< -float(okex_api.get_current_price(coinname)[0]['last'])/100:
        buyState = True
        zs_price = prices[2][-5:].min()

    if red_line[-2]>yellow_line[-2] and red_line[-1]<yellow_line[-1] and red_line[-1] > float(okex_api.get_current_price(coinname)[0]['last'])/100:
        sellState = True
        zs_price = prices[1][-5:].max() 
    return buyState, sellState, zs_price, red_line, yellow_line

def hand_state(coinname, timetick):
    kline = okex_api.get_price(coinname, timetick, "1", 7)
    #pdb.set_trace()
    TradingVolume, prices = okex_api.kline_rank(kline)
    close_price = np.hstack([prices[0], float(okex_api.get_current_price(coinname)[0]['last'])])
    red_line, yellow_line, sh = index.Impulse_MACD(prices, lengthMA=34, lengthSignal=9)
    EMA12, EMA25, EMA200, MACD = coin_state(close_price)
    buyState = False
    sellState = False
    if EMA12[-2] < EMA25[-2] and EMA12[-1] > EMA25[-1] or red_line[-1]>yellow_line[-1]:
        buyState = True
    if EMA12[-2] > EMA25[-2] and EMA12[-1] < EMA25[-1] or red_line[-1]<yellow_line[-1]:
        sellState = True

    return buyState, sellState

def sample_test(instId, sz, sz1):
    filename = 'trading_info.txt'
    tdMode = "isolated" #交易模式
    lever = "10" # 杠杆倍数
    
    #print(okex_api.intTodatetime(int(time.time()* 1000+8 * 3600 * 1000)), instId, ',buyState:', buyState, ',sellState:', sellState)
    if okex_api.getPositions(instId)['data'][0]['pos'] == '0':
        para = {}
        buyState, sellState, zs_price, red_line, yellow_line = order_index(instId, '15m')
        #okex_api.set_leverage(instId, lever, tdMode)
        ids = str(random.randint(0,100000))
        if sellState == True:
            para['coinname'] = instId
            para['timetick'] = '15m'
            para['zs_price'] = zs_price
            para['side'] = 'sell'
            para['ids'] = ids
            para['time'] = okex_api.intTodatetime(int(time.time()* 1000+8 * 3600 * 1000))
            para['zy_price'] =  2.5*float(okex_api.get_current_price(instId)[0]['last']) - 1.5*zs_price 
            result = json.dumps(para)
        #    okex_api.create_order(instId, tdMode, para['side'], sz, ids)
            okex_api.dingding_alarm2(result)
        if buyState == True:
            para['coinname'] = instId
            para['timetick'] = '15m'
            para['zs_price'] = zs_price
            para['side'] = 'buy'
            para['ids'] = ids
            para['time'] = okex_api.intTodatetime(int(time.time()* 1000+8 * 3600 * 1000))
            para['zy_price'] = 2.5*float(okex_api.get_current_price(instId)[0]['last']) - 1.5*zs_price 
            result = json.dumps(para)
        #    okex_api.create_order(instId, tdMode, para['side'], sz, ids)
            okex_api.dingding_alarm2(result)

        buyState, sellState, zs_price, red_line, yellow_line = order_index(instId, '1H')
        para = {}
        #okex_api.set_leverage(instId, lever, tdMode)
        ids = str(random.randint(0,100000))
        if sellState == True:
            para['coinname'] = instId
            para['timetick'] = '1H'
            para['zs_price'] = zs_price
            para['side'] = 'sell'
            para['ids'] = ids
            para['time'] = okex_api.intTodatetime(int(time.time()* 1000+8 * 3600 * 1000))
            para['zy_price'] =  2.5*float(okex_api.get_current_price(instId)[0]['last']) - 1.5*zs_price 
            result = json.dumps(para)
        #    okex_api.create_order(instId, tdMode, para['side'], sz, ids)
            okex_api.dingding_alarm2(result)
        if buyState == True:
            para['coinname'] = instId
            para['timetick'] = '1H'
            para['zs_price'] = zs_price
            para['side'] = 'buy'
            para['ids'] = ids
            para['time'] = okex_api.intTodatetime(int(time.time()* 1000+8 * 3600 * 1000))
            para['zy_price'] = 2.5*float(okex_api.get_current_price(instId)[0]['last']) - 1.5*zs_price 
            result = json.dumps(para)
        #    okex_api.create_order(instId, tdMode, para['side'], sz, ids)
            okex_api.dingding_alarm2(result)
        buyState, sellState, zs_price, red_line, yellow_line = order_index(instId, '4H')
        #okex_api.set_leverage(instId, lever, tdMode)
        para = {}
        ids = str(random.randint(0,100000))
        if sellState == True:
            para['coinname'] = instId
            para['timetick'] = '4H'
            para['zs_price'] = zs_price
            para['side'] = 'sell'
            para['ids'] = ids
            para['time'] = okex_api.intTodatetime(int(time.time()* 1000+8 * 3600 * 1000))
            para['zy_price'] =  2.5*float(okex_api.get_current_price(instId)[0]['last']) - 1.5*zs_price 
            result = json.dumps(para)
        #    okex_api.create_order(instId, tdMode, para['side'], sz, ids)
            okex_api.dingding_alarm2(result)
        if buyState == True:
            para['coinname'] = instId
            para['timetick'] = '4H'
            para['zs_price'] = zs_price
            para['side'] = 'buy'
            para['ids'] = ids
            para['time'] = okex_api.intTodatetime(int(time.time()* 1000+8 * 3600 * 1000))
            para['zy_price'] = 2.5*float(okex_api.get_current_price(instId)[0]['last']) - 1.5*zs_price 
            result = json.dumps(para)
        #    okex_api.create_order(instId, tdMode, para['side'], sz, ids)
            okex_api.dingding_alarm2(result)
        #if len(para) >0:
        #    f2 = open(instId+'.json', 'w')
        #    f2.write(result)
        #    f2.close()
        
def trading():
    sample_test('ETC-USDT-SWAP','6','2')
    sample_test('BTC-USDT-SWAP','6','2')
    sample_test('FIL-USDT-SWAP','2100','700')
    sample_test('LTC-USDT-SWAP','120','40')
    sample_test('CFX-USDT-SWAP','300','100')
    sample_test('OP-USDT-SWAP','510','170')
    sample_test('CRV-USDT-SWAP','1200','400')
    sample_test('ATOM-USDT-SWAP','60','20')
    sample_test('ONT-USDT-SWAP','60','20')
    sample_test('ETH-USDT-SWAP','9','3')




        
        
def get_trading_loop():
    schedule.every(1).seconds.do(trading)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception:
            err = traceback.format_exc().replace("\n", "|||")
            print(err)



get_trading_loop()
