import okex_api
import ATR



kline = okex_api.get_price('BTC-USDT-SWAP', '15m', "1", 7)
TradingVolume, prices = okex_api.kline_rank(kline)
ATR.cal_ATR(prices, 22)