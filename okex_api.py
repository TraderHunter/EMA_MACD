# encoding: utf-8
"""
@author:  lingxiao he
@contact: xiaomingzhidao1@gmail.com
"""

from hashlib import sha256
import hmac
import base64
import pytz
import time
import datetime
import traceback
import requests
import json
import schedule
import codecs
import pdb
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from tqdm import tqdm
import time_trans

apikey = "9c8450f2-6ed1-4699-a087-08a995d97906"
secretkey = "D59CCA83D6391E7319F679C056DE6326"
Passphrase ="Hlx371240!"
rootUrl="https://aws.okx.com"
def get_sign(secretkey, data):
    _key = secretkey.encode('utf-8')
    _data = data.encode('utf-8')
    sign = hmac.new(_key,_data, digestmod=sha256)
    sign= base64.b64encode(sign.digest())
    sign = sign.decode()
    return sign
	

#OK-ACCESS-KEY字符串类型的APIKey。
#OK-ACCESS-SIGN使用HMAC SHA256哈希函数获得哈希值，再使用Base-64编码（请参阅签名）。
#OK-ACCESS-TIMESTAMP发起请求的时间（UTC），如：2020-12-08T09:08:57.715Z
#OK-ACCESS-PASSPHRASE您在创建API密钥时指定的Passphrase。

#签名
#生成签名
#OK-ACCESS-SIGN的请求头是对timestamp + method + requestPath + body字符串（+表示字符串连接），以及SecretKey，使用HMAC SHA256方法加密，通过Base-64编码输出而得到的。
#如：sign=CryptoJS.enc.Base64.stringify(CryptoJS.HmacSHA256(timestamp + 'GET' + '/api/v5/account/balance?ccy=BTC', SecretKey))
#其中，timestamp的值与OK-ACCESS-TIMESTAMP请求头相同，为ISO格式，如2020-12-08T09:08:57.715Z。
#method是请求方法，字母全部大写：GET/POST。
#requestPath是请求接口路径。如：/api/v5/account/balance
#body是指请求主体的字符串，如果请求没有主体（通常为GET请求）则body可省略。如：{"instId":"BTC-USDT","lever":"5","mgnMode":"isolated"}

def createHead(method,requestPath,body):
    headers = {'Content-Type': 'application/json',"OK-ACCESS-KEY":apikey}
    #headers = {'Content-Type': 'application/json',"x-simulated-trading":"1","OK-ACCESS-KEY":apikey}
    d=datetime.datetime.now(pytz.timezone('utc'))
    ts = datetime.datetime.strftime(d,"%Y-%m-%dT%H:%M:%SZ")
    headers["OK-ACCESS-TIMESTAMP"] = ts
    headers["OK-ACCESS-PASSPHRASE"] = Passphrase
    method = method.upper()
    data = ts+method+requestPath
    if method == "POST":
        data = data+ body
    sign = get_sign(secretkey,data)
    #print(data)
    headers["OK-ACCESS-SIGN"] = sign
    #print(headers)
    return headers

def dingding_alarm1(msg):
    """
    钉钉机器人报警函数。
    """
    url = 'https://oapi.dingtalk.com/robot/send?access_token=f747ce8393070c56c6bbb414e827e5fdd287d9d14b032c801b8795563e6cb491'

    data = {
        "msgtype": "text",
        "text": {
            "content": "EMAtrading:%s" % msg
        }
    }
    headers = {'content-type': "application/json"}
    requests.post(url, json.dumps(data).encode('utf-8'), headers=headers)

def dingding_alarm2(msg):
    """
    钉钉机器人报警函数。
    """
    url = 'https://oapi.dingtalk.com/robot/send?access_token=a2536fbf0ef75fc6efa0459fd2d56a18fb337dab337212e2af7a925e7f752e02'

    data = {
        "msgtype": "text",
        "text": {
            "content": "xiaobo:%s" % msg
        }
    }
    headers = {'content-type': "application/json"}
    requests.post(url, json.dumps(data).encode('utf-8'), headers=headers)	

def doGet(url):
    for i in range(1):
        try:
            headers = createHead("get",url,None)
            response = requests.get(rootUrl + url,headers=headers)
            #pdb.set_trace()
            #print(response,response.text)
            if response.status_code == 200:
                res = json.loads(response.text)
                return res
            else:
                return {"code":400,"msg":"Wrong Response Code"} 
        except Exception as e:
            err = traceback.format_exc()
            print(err)
    return None
def doPost(url,body):
    for i in range(1):
        try:
            data = json.dumps(body)
            headers = createHead("post",url,data)
            response = requests.post(rootUrl + url,headers=headers,data=data)
            if response.status_code == 200:
                res = json.loads(response.text)
                return res
            else:
                return {"code":400,"msg":"Wrong Response Code"} 
        except Exception as e:
            err = traceback.format_exc()
            print(err)
    return None
def getHistory():
    url= "/api/v5/trade/fills"
    return doGet(url)
def getBalance():
    url= "/api/v5/account/balance"
    return doGet(url)      
def getAllPrice():
 
    url = "/api/v5/market/tickers?instType=SWAP"
    return doGet(url)
def getPositions(instId):
    url = "/api/v5/account/positions?instType=SWAP"+"&instId="+instId
    return doGet(url)   

def getallPositions():
    #pdb.set_trace()
    url = "/api/v5/account/positions?instType=SWAP"
    return doGet(url) 

def closePosition(instId):
    url = "/api/v5/trade/close-position"
    body = {}
    body['instId'] = instId
    body['mgnMode'] = "isolated"
    return doPost(url, body)


def create_order(instId,tdMode,side,sz,clOrdId):
    url = "/api/v5/trade/order"
    body = {}
    body["instId"] = instId
    body["tdMode"] = tdMode
    body["side"] = side
    body["ordType"] = "optimal_limit_ioc"
    body["sz"] = sz
    #body["px"] = px
    body["clOrdId"] = clOrdId
    return doPost(url,body)

def intTodatetime(intValue):
	if len(str(intValue)) == 10:
		# 精确到秒
		timeValue = time.localtime(intValue)
		tempDate = time.strftime("%Y-%m-%d %H:%M:%S", timeValue)
		datetimeValue = datetime.datetime.strptime(tempDate, "%Y-%m-%d %H:%M:%S")
	elif 10 <len(str(intValue)) and len(str(intValue)) < 15:
		# 精确到毫秒
		k = len(str(intValue)) - 10
		timetamp = datetime.datetime.fromtimestamp(intValue/(1* 10**k))
		datetimeValue = timetamp.strftime("%Y-%m-%d %H:%M:%S.%f")
	else:
		return -1
	return datetimeValue
def create_order_algo(instId,maxPx,minPx,gridNum,runType,tpTriggerPx,slTriggerPx,sz,direction,lever,basePos,tag):
    url = "/api/v5/tradingBot/grid/order-algo"

    body = {}
    body["instId"] = instId
    body["algoOrdType"] = "contract_grid"
    body["maxPx"] = maxPx
    body["minPx"] = minPx
    body["gridNum"] = gridNum
    body["runType"] = runType
    body["tpTriggerPx"] = tpTriggerPx
    body["slTriggerPx"] = slTriggerPx
    body["sz"] = sz
    body["direction"] = direction
    body["lever"] = lever
    body["basePos"] = basePos
    body["tag"] = tag
    return doPost(url,body)

def set_leverage(instId, lever, mgnMode):
    url = "/api/v5/account/set-leverage"
    body = {}
    #pdb.set_trace()
    body["instId"] = instId
    body["lever"] = lever
    body["mgnMode"] = mgnMode
    #pdb.set_trace()
    return doPost(url,body)
    
def stop_order_algo(algoId,instId):
    url = "/api/v5/tradingBot/grid/stop-order-algo"
    body = {}
    body["algoId"] = algoId
    body["instId"] = instId
    body["algoOrdType"] = "contract_grid"
    body["stopType"] = "1"
    return doPost(url,[body])


def modify_order_algo(algoId,instId,tpTriggerPx,slTriggerPx):
    url = "/api/v5/tradingBot/grid/amend-order-algo"

    body = {}
    body["algoId"] = algoId
    body["instId"] = instId
    body["tpTriggerPx"] = tpTriggerPx
    body["slTriggerPx"] = slTriggerPx
    return doPost(url,body)

def get_current_price(instId):
    url = "/api/v5/market/ticker?instId=" + instId

    current_price = doGet(url)
    if current_price is not None:
        current_price = current_price['data']

    return current_price

def get_price(instId, timetick, begintime, day_num):
    """
    获取历史的k线，收盘价、最低价、最高价、开盘价。

    参数：
    instId: 标的的代码。
    timetick: 时间粒度，如5m/15m/30m/1H/4H/1D/1W。
    day_num: 需要计算天数

    返回：
    List[float]，K线序列。
    """
    #print(instId, timetick, begintime, day_num)
    if begintime == "1":
        t = int(time.time()* 1000)
    else:
        t = int(time_trans.time_to_unix(begintime)) * 1000
    #Id = instId.split('-')[0] + '-'+ instId.split('-')[1]
    dataTotal= []
    for i in range(day_num):
        for j in range(10):
            start = t - (day_num - i) * 24 * 3600 * 1000
            end = t - (day_num - i - 1) *24 * 3600 * 1000
            #pdb.set_trace()
            url= "/api/v5/market/history-candles?limit=100&bar="+timetick+"&instId=" + instId + "&before=" + str(start) + "&after=" + str(end)
            x = doGet(url)
            if "data" not in x:
                time.sleep(1)
                continue
            dataTotal += x["data"]
            break
        
    return dataTotal



def kline_rank(kline):
    TradingVolume = []
    TimeTick = []
    ClosePrice = []
    HighPrice = []
    LowPrice = []
    for i in range(len(kline)):
        TimeTick.append(int(kline[i][0]))
        TradingVolume.append(float(kline[i][7]))
        ClosePrice.append(float(kline[i][4]))
        HighPrice.append(float(kline[i][2]))
        LowPrice.append(float(kline[i][3]))
    #pdb.set_trace()
    index = np.argsort(np.array(TimeTick))
    TradingVolume = np.array(TradingVolume)[index]
    ClosePrice = np.array(ClosePrice)[index]
    HighPrice = np.array(HighPrice)[index]
    LowPrice = np.array(LowPrice)[index]

    return TradingVolume, [ClosePrice, HighPrice, LowPrice]


def get_seven_15m_ATR(instId):
    url="/api/v5/market/ticker?instId=" + instId #+ "-SWAP"
    #pdb.set_trace()
    data = doGet(url)
    if data is not None:
        data = data["data"]
    t = int(time.time()* 1000)
    Id = instId.split('-')[0] + '-'+ instId.split('-')[1]
    #pdb.set_trace()
    start = t - 15 * 7 * 60 * 1000
    end = t
    url= "/api/v5/market/index-candles?limit=100&bar=15m&instId=" + Id + "&before=" + str(start) + "&after=" + str(end)
    dataTotal = doGet(url)["data"]
    ATR = []
    for i in range(len(dataTotal)):
        ATR.append(float(dataTotal[i][2]) - float(dataTotal[i][3]))

    return {"ATR":np.array(ATR).mean(), "current":data}


def normalization(data):
    _range = np.max(data) - np.min(data)
    return (data - np.min(data)) / _range

## 计算各种币种的波动参数、网格数量、上下界限
def cal_klines_vol(coin_name):
    instId = coin_name
    data = getPrice(instId)
    k15_data, current_data = data['k15'], data['current']
    para_dict = {}
    open_price = []
    high_price = []
    low_price = []
    close_price = []
    bd_ratio = [] #波动率
    ATR = [] #绝对波动值
    price = [] # 开高低收
    for i in range(len(k15_data)):
        open_price.append(float(k15_data[i][1]))
        high_price.append(float(k15_data[i][2]))
        low_price.append(float(k15_data[i][3]))
        close_price.append(float(k15_data[i][4]))

        #bd_direction.append()
        price.append((float(k15_data[i][1])+float(k15_data[i][2])+float(k15_data[i][3])+float(k15_data[i][4]))/4)
        #pdb.set_trace()
        if i+1<len(k15_data):
                bd_ratio.append(100*(max(float(k15_data[i+1][2]), float(k15_data[i][2]))-min(float(k15_data[i+1][3]), float(k15_data[i][3])))/float(k15_data[i+1][4]))
        if (float(k15_data[i][2]) - float(k15_data[i][3]))/float(k15_data[i][1]) >= 0.008:
            ATR.append(float(k15_data[i][2]) - float(k15_data[i][3]))
    peaks = signal.find_peaks(np.array(price))[0]
    #pdb.set_trace()
    
    #test_fft(np.array(price), coin_name)
    #pdb.set_trace()
    volatility = abs(100 * (np.array(price)[peaks][2:] - np.array(price)[peaks][1:-1])/np.array(price)[peaks][2:])
    peak_bd = volatility[np.where(volatility >= 2)[0]].mean()
    mean_price = np.array(open_price).mean()
    #pdb.set_trace()
    bottom_price = np.array(low_price).min()
    up_price = np.array(high_price).max()
    para_dict['coin_name'] = coin_name
    para_dict['ATR'] = np.array(ATR).mean()
    para_dict['up_price'] = up_price + 5 * para_dict['ATR']
    para_dict['bottom_price'] = bottom_price - 5 * para_dict['ATR']
    para_dict['peak_num'] = len(np.where(volatility > 2)[0])
    #pdb.set_trace()
    last_price = float(current_data[0]['last'])
    para_dict['last_price'] = last_price
    if up_price - last_price > last_price-bottom_price:
        para_dict['long_ratio'] = (last_price-bottom_price)/(up_price - last_price)
        para_dict['short_ratio'] = 1
    if (last_price-bottom_price) > (up_price - last_price):
        para_dict['long_ratio'] = 1
        para_dict['short_ratio'] = (up_price - last_price)/(last_price-bottom_price)

    para_dict['up_ratio'] = min(up_price - last_price,last_price-bottom_price)/max(up_price - last_price,last_price-bottom_price)
    if mean_price - last_price > 0:
        para_dict['bottom_price'] = para_dict['bottom_price'] -  (mean_price - last_price)
    if mean_price - last_price < 0:
        para_dict['up_price'] = para_dict['up_price'] + last_price - mean_price 
    para_dict['net_num'] = (para_dict['up_price'] - para_dict['bottom_price'])/para_dict['ATR']
    para_dict['bd_ratio'] = np.array(bd_ratio).mean()*0.7 + peak_bd * 0.3
    para_dict['price_var'] = np.var(normalization(price))
    #print(para_dict)
    return para_dict


def cal_klines_1d(coin_name):
    instId = coin_name
    k15_data = get1DPrice(instId)

    para_dict = {}
    open_price = []
    high_price = []
    low_price = []
    close_price = []
    bd_ratio = [] #波动率
    ATR = [] #绝对波动值
    price = [] # 开高低收
    for i in range(len(k15_data)):
        open_price.append(float(k15_data[i][1]))
        high_price.append(float(k15_data[i][2]))
        low_price.append(float(k15_data[i][3]))
        close_price.append(float(k15_data[i][4]))
        #pdb.set_trace()
        bd_ratio.append(100*(float(k15_data[i][2]) - float(k15_data[i][3]))/float(k15_data[i][1]))
        #bd_direction.append()  
    para_dict['coin_name'] = coin_name
    para_dict['bd_ratio'] = np.array(bd_ratio).mean()
    #print(para_dict)
    return para_dict

def bd_rank1():
    #print('select coin running...')
    coin_name = []
    result = []
    data = getAllPrice()['data']
    for i in range(len(data)):
        coin_name.append(data[i]['instId'])
    for i in tqdm(range(len(coin_name))):
        coinname = coin_name[i]
        if coinname.split('-')[1] == 'USDT':
            dict = cal_klines_1d(coinname)
            result.append(dict)
    bd = []
    for i in range(len(result)):
        bd.append(result[i]['bd_ratio'])
    bd = np.array(bd)
    index = np.argsort(-bd)
    select_coin = []
    for i in range(0,30):
        print(result[index[i]])
    return select_coin

## 选择波动最大的10个币种
def bd_rank():
    #print('select coin running...')
    coin_name = []
    result = []
    data = getAllPrice()['data']
    for i in range(len(data)):
        coin_name.append(data[i]['instId'])
    for i in tqdm(range(len(coin_name))):
        coinname = coin_name[i]
        if coinname.split('-')[1] == 'USDT':
            dict = cal_klines_vol(coinname)
            result.append(dict)
    bd = []
    for i in range(len(result)):
        bd.append(result[i]['bd_ratio'])
    bd = np.array(bd)
    index = np.argsort(-bd)
    select_coin = []
    for i in range(0,30):
        if result[index[i]]['long_ratio'] <= 0.25 or result[index[i]]['short_ratio'] <= 0.25 and result[index[i]]['price_var'] >=0.04:
            select_coin.append(result[index[i]])
    return select_coin

def auto_trading():
    ## 查看是否有持仓
    current_order = getPositions()
    #
    
    if current_order['data'] == []:
        print("Order is empty, select coin and create contact_grid")
        coins = bd_rank()
        selected_coin = coins[0]
        #pdb.set_trace()
        runType="1"
        instId, maxPx, minPx, gridNum, tpTriggerPx, slTriggerPx, sz = selected_coin['coin_name'],selected_coin['up_price'],selected_coin['bottom_price'], str(int(selected_coin['net_num'])), str(float(selected_coin['bottom_price'])-0.01),str(float(selected_coin['up_price'])+0.01), str(float(getBalance()['data'][0]['details'][0]['availEq'])/3)
        create_order_algo(instId, maxPx, minPx, gridNum, runType, tpTriggerPx, slTriggerPx, sz, direction="short",lever="10",basePos=True,tag="wclalgo002")
        create_order_algo(instId, maxPx, minPx, gridNum, runType, slTriggerPx, tpTriggerPx, sz, direction="long",lever="10",basePos=True,tag="wclalgo001")
    print(time.time(), "current_coin:", current_order['data'][0]['instId'], "totalPnl:", (float(getBalance()['data'][0]['details'][0]['eq'])-5000)*100/5000)
    stgyEq = float(getBalance()['data'][0]['details'][0]['stgyEq'])
    dict = cal_klines_vol(current_order['data'][0]['instId'])
    if dict['price_var'] < 0.04 and dict[up_down_ratio] <= 0.3 and (float(current_order['data'][0]['totalPnl'])+float(current_order['data'][1]['totalPnl']))/stgyEq > 0.1:
        for i in range(0,1):
            algoId, instId = current_order['data'][i]['algoId'], current_order['data'][i]['instId']
            stop_order_algo(algoId, instId)
    elif (float(current_order['data'][0]['totalPnl'])+float(current_order['data'][1]['totalPnl']))/stgyEq > 0.25:
        for i in range(0,1):
            algoId, instId = current_order['data'][i]['algoId'], current_order['data'][i]['instId']
            stop_order_algo(algoId, instId)        



         
    
    

def get_trading_loop():
    schedule.every(1).second.do(auto_trading)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception:
            err = traceback.format_exc().replace("\n", "|||")
            print(err)

