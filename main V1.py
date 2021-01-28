from binance.client import Client
from binance.enums import *
import json
import os
import websocket
import numpy
import talib
import pprint # used to print message later on if I to use it

API_KEY = os.environ.get('uXkyxhX91JRTUiUooBnL4rftknzxpkVPAs4VgCz4GKJVHDrLeJpIXfGTQ9fhvjgn')
API_SECRET = os.environ.get('VZU35Wi86GnwALkY36CM1cYjK1CVZrXA7Nt2RD6BdyWlcOUgImjWAPV0arSVCwCZ')
client = Client(API_KEY, API_SECRET)

candles = client.get_klines(symbol='ETHUSDT', interval=Client.KLINE_INTERVAL_1MINUTE)
price_of_opens = []
volume_of_closes = []
price_of_closes = []
price_of_highs = []
price_of_lows = []
for x in candles:
  price_of_closes.append(x[4])
  price_of_highs.append(x[2])
  price_of_lows.append(x[3])
  volume_of_closes.append(x[8])
  price_of_opens.append(x[1])

def removingapos(x):
    for Index, Float in enumerate(x): x[Index] = float(Float)

removingapos(price_of_closes)
removingapos(volume_of_closes)
removingapos(price_of_highs)
removingapos(price_of_lows)
removingapos(price_of_opens)
rsi_period = 14
rsi_overbought = 65
rsi_oversold = 30
symbol = 'ETHUSD'
ETH_QUANTITY = 0.01
in_position = False

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("Exception:")
        print(e)
        return False

    return True

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

def on_open(websocket):
    print("connection opened")
def on_close(websocket):
    print("connection closed")
def on_message(websocket, message, in_position=False):
    message = json.loads(message)
    # converting message using json and using data from websockets
    candle_stick = message['k']
    candle_true = candle_stick['x']
    price_of_close = candle_stick['c']
    volume_of_close = candle_stick['v']
    price_of_high = candle_stick['h']
    price_of_low = candle_stick['l']
    price_of_open = candle_stick['o']

    if candle_true:
        price_of_closes.append(float(price_of_close))
        volume_of_closes.append(float(volume_of_close))
        price_of_highs.append(float(price_of_high))
        price_of_lows.append(float(price_of_low))
        price_of_opens.append(float(price_of_open))
# option to print alot of data        pprint.pprint(message)

        print("Closing price:", price_of_closes[-5:])
        np_closes = numpy.array(price_of_closes)
        rsi = talib.RSI(np_closes, rsi_period)
        current_rsi = rsi[-1]
        print("RSI:", current_rsi)

        np_prices = numpy.array(price_of_closes)
        np_volume = numpy.array(volume_of_closes)
        np_price_high = numpy.array(price_of_highs)
        np_price_low = numpy.array(price_of_lows)
        np_price_open = numpy.array(price_of_opens)  # this is needed if I use Pattern recognition in talib

        macd, macdsignal, macdhist = talib.MACD(np_prices, fastperiod=12, slowperiod=26, signalperiod=9)
        print("Current MACD, signal, hist value:", macd[-1], macdsignal[-1], macdhist[-1])

        real_obv = talib.OBV(np_prices, np_volume)
        print("On Balance Volume:", real_obv[-1])

        real_atr = talib.ATR(np_price_high, np_price_low, np_prices, timeperiod=14)
        print("ATR:", real_atr[-1])

        ADX = talib.ADX(np_price_high, np_price_low, np_prices, timeperiod=14)
        print("ADX:", ADX[-1])

        AD = talib.AD(np_price_high, np_price_low, np_prices, np_volume)
        print("AD:", AD[-1])

        ADOSC = talib.ADOSC(np_price_high, np_price_low, np_prices, np_volume, fastperiod=3, slowperiod=10)
        print("ADOSC:", ADOSC[-1])

        TRANGE = talib.TRANGE(np_price_high, np_price_low, np_prices)
        print("TRANGE:", TRANGE[-1])
        position_value = []
        if current_rsi < rsi_oversold:
            print("1")
            if macd[-1] < -1:
                print("2")
                if macdsignal[-1] < 0:
                    print("4")
                    if real_atr[-14] < real_atr[-1]:
                        print("5")
                        if ADOSC[-14] < ADOSC[-1]:
                            print("6")
                            if ADX[-1] < 0:
                                print("7")
                                if TRANGE[-14] < TRANGE[-1]:
                                    print("8")
                                    if in_position:
                                        print("OverSold - Already Purchased")
                                    else:
                                        print("Oversold - Purchase")
                                        order_succeeded = order(SIDE_BUY, ETH_QUANTITY, symbol)
                                        if order_succeeded:
                                            position_value.append(price_of_closes[-1])
                                            in_position = True
        if current_rsi > rsi_overbought:
            if macd > 1:
                if macdsignal > 0:
                    if real_atr[-14] > real_atr[-1]:
                        if ADOSC[-14] > ADOSC[-1]:
                            if ADX > 5:
                                if TRANGE[-14] > TRANGE[-1]:
                                    if (ETH_QUANTITY * position_value[-1]) < (ETH_QUANTITY * price_of_closes[-1]):
                                        if in_position:
                                            print("Overbought - Sell")
                                            order_succeeded = order(SIDE_SELL, ETH_QUANTITY, symbol)
                                            if order_succeeded:
                                                in_position = False

websocket = websocket.WebSocketApp(SOCKET , on_open=on_open, on_close=on_close, on_message=on_message)
websocket.run_forever()