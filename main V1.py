from contextlib import redirect_stdout
from binance.client import Client
from binance.enums import *
import json
import os
import websocket
import numpy
import talib
import datetime
import pytz

time = datetime.datetime.now()
timezone = pytz.timezone("Europe/Paris")
currentTime = timezone.localize(time)

import pprint # used to print message later on if I to use it
API_KEY = os.environ.get('uXkyxhX91JRTUiUooBnL4rftknzxpkVPAs4VgCz4GKJVHDrLeJpIXfGTQ9fhvjgn')
API_SECRET = os.environ.get('VZU35Wi86GnwALkY36CM1cYjK1CVZrXA7Nt2RD6BdyWlcOUgImjWAPV0arSVCwCZ')
client = Client(API_KEY, API_SECRET)

SOCKET_ETH = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

in_position = False

def on_open(websocket):
    print("connection opened")
def on_close(websocket):
    print("connection closed")
def on_message(websocket, message, symbol_used='ETHUSDT'):
    global in_position
    rsi_period = 14
    rsi_overbought = 60
    rsi_oversold = 28
    ETH_QUANTITY = 1
    percent_gain = 1.01
    candles = client.get_historical_klines(symbol_used, Client.KLINE_INTERVAL_1MINUTE, "1 day ago GMT+1")
    price_of_closes_7_days = []
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

    def removingapos(apos_input):
        for Index, Float in enumerate(apos_input): apos_input[Index] = float(Float)

    removingapos(price_of_closes)
    removingapos(volume_of_closes)
    removingapos(price_of_highs)
    removingapos(price_of_lows)
    removingapos(price_of_opens)

    def order(side, quantity, symbol_used, order_type=ORDER_TYPE_MARKET):
        try:
            print("sending order")
            order = client.create_order(symbol=symbol_used, side=side, type=order_type, quantity=quantity)
            print(order)
        except Exception as e:
            print("Exception:")
            print(e)
            return False

        return True
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

        macd6, macdsignal6, macdhist6 = talib.MACD(np_prices[-1440:], fastperiod=300, slowperiod=650, signalperiod=225)
        print("Current MACD, signal, hist value 6 hours:", macd6[-1], macdsignal6[-1], macdhist6[-1])

        macd, macdsignal, macdhist = talib.MACD(np_prices[-1440:], fastperiod=12, slowperiod=26, signalperiod=9)
        print("Current MACD, signal, hist value:", macd[-1], macdsignal[-1], macdhist[-1])

        obv = talib.OBV(np_prices[-1440:], np_volume[-1440:])
        print("On Balance Volume:", obv[-1])

        real_atr = talib.ATR(np_price_high[-1440:], np_price_low[-1440:], np_prices[-1440:], timeperiod=14)
        print("ATR:", real_atr[-1])

        ADX = talib.ADX(np_price_high[-1440:], np_price_low[-1440:], np_prices[-1440:], timeperiod=14)
        print("ADX:", ADX[-1])

        AD = talib.AD(np_price_high[-1440:], np_price_low[-1440:], np_prices[-1440:], np_volume[-1440:])
        print("AD:", AD[-1])

        ADOSC = talib.ADOSC(np_price_high[-1440:], np_price_low[-1440:], np_prices[-1440:], np_volume[-1440:], fastperiod=3, slowperiod=10)
        print("ADOSC:", ADOSC[-1])

        TRANGE = talib.TRANGE(np_price_high[-1440:], np_price_low[-1440:], np_prices[-1440:])
        print("TRANGE:", TRANGE[-1])
        position_value = []
        data = price_of_closes[-1]
        def avgcalc(x):
            g1 = (x[-2] + x[-3] + x[-4] + x[-5] + x[-6])/5
            return g1
        if macd[-1] < -2.5 and macd[-1] < (avgcalc(macd[-1])):
            if macd6[-1] < 0:
                if obv[-1] < -25000:
                    rsi_oversold = 25
                if obv[-1] < -20000:
                    rsi_oversold = 20
                if obv[-1] < -15000:
                    rsi_oversold = 17.5
                if obv[-1] < -10000:
                    rsi_oversold = 15
                if obv[-1] < -7500:
                    rsi_oversold = 12
            if current_rsi < rsi_oversold:
                if in_position:
                    print("Oversold - Already Purchased")
                else:
                    print("Oversold - Purchase")
                    tuple_num = ("Buy - Price", "Price:", data, "MACD:", macd[-1], "OBV:", obv[-1], "Time:", "TRANGE:", TRANGE[-1], "ADOSC:", ADOSC[-1], "ATR:", real_atr[-1], "ADX:", ADX[-1], currentTime)
                    with open('BuySellData.txt', 'a') as f:
                        with redirect_stdout(f):
                            print(tuple_num)
                    position_value.append(price_of_closes[-1])
                    in_position = True

                        # for testing purposes
                        #order_succeeded = order(SIDE_BUY, ETH_QUANTITY, symbol_used)
                                #if order_succeeded:
                                    #position_value.append(price_of_closes[-1])
                                    #in_position = True

        if current_rsi > rsi_overbought:
            if macd6[-1] > 2:
                if obv[-1] < 25000:
                    percent_gain = 1.015
                elif obv[-1] < 20000:
                    percent_gain = 1.02
            print("1")
            if (ETH_QUANTITY * position_value[-1]) > ((ETH_QUANTITY * price_of_closes[-1]) * percent_gain):
                print("2")
                while True:
                    if in_position:
                        print("Sell- Price")
                        tuple_num = ("Sell - Price", "Price:", data, "MACD:", macd[-1], "OBV:", obv[-1], "Time:", "TRANGE:", TRANGE[-1], "ADOSC:", ADOSC[-1], "ATR:", real_atr[-1], "ADX:", ADX[-1], currentTime)
                        with open('BuySellData.txt', 'a') as f:
                            with redirect_stdout(f):
                                print(tuple_num)
                        in_position = False
                        # order_succeeded = order(SIDE_SELL, ETH_QUANTITY, symbol_used)
                        # if order_succeeded:
                        # in_position = True

                    else:
                        print("Don't own any ETH")


websocket = websocket.WebSocketApp(SOCKET_ETH , on_open=on_open, on_close=on_close, on_message=on_message)
websocket.run_forever()
