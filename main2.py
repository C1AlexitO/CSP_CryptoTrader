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
import sys
sys.setrecursionlimit(1000000)

API_KEY = os.environ.get('API_Key')
API_SECRET = os.environ.get('API_Secret')
client = Client(API_KEY, API_SECRET)

in_position = False
symbol_used='ETHUSDT'
candles = client.get_historical_klines(symbol_used, Client.KLINE_INTERVAL_1MINUTE, "2 days ago GMT+1")
candles.reverse()
rsisave = []
h = -50
def thing():
        global in_position, candles, h, rsisave
        h = h - 1
        rsi_period = 14
        rsi_overbought = 71
        rsi_oversold = 25
        price_of_closes_7_days = []
        price_of_opens = []
        volume_of_closes = []
        price_of_closes = []
        price_of_highs = []
        price_of_lows = []
        inttime = []
        # appending historical data to these list
        for x in candles:
            inttime.append(x[0])
            price_of_closes.append(x[4])
            price_of_highs.append(x[2])
            price_of_lows.append(x[3])
            volume_of_closes.append(x[8])
            price_of_opens.append(x[1])

        # function to remove apostrophes
        def removingapos(apos_input):
            for Index, Float in enumerate(apos_input): apos_input[Index] = float(Float)

        removingapos(inttime)
        removingapos(price_of_closes)
        removingapos(volume_of_closes)
        removingapos(price_of_highs)
        removingapos(price_of_lows)
        removingapos(price_of_opens)
        np_prices = numpy.array(price_of_closes[h:])
        np_volume = numpy.array(volume_of_closes[h:])
        np_price_high = numpy.array(price_of_highs[h:])
        np_price_low = numpy.array(price_of_lows[h:])
        np_price_open = numpy.array(price_of_opens[h:])
        rsi = talib.RSI(np_prices, rsi_period)
        current_rsi = rsi[h+14]

        # Using TA-Lib to get indicators to purchase or sell and printing them out to console

        macd, macdsignal, macdhist = talib.MACD(np_prices[h:], fastperiod=12, slowperiod=26, signalperiod=9)
        obv = talib.OBV(np_prices[h:], np_volume[h:])
        real_atr = talib.ATR(np_price_high[h:], np_price_low[h:], np_prices[h:], timeperiod=14)
        AD = talib.AD(np_price_high[h:], np_price_low[h:], np_prices[h:], np_volume[h:])
        TRANGE = talib.TRANGE(np_price_high[h:], np_price_low[h:], np_prices[h:])
        MFI = talib.MFI(np_price_high[h:], np_price_low[h:], np_prices[h:], np_volume[h:], timeperiod=14)
        currentTime = datetime.datetime.fromtimestamp(inttime[h] / 1e3)
        position_value = []
        position_value.append(price_of_closes[h])
        removingapos(position_value)
        data = price_of_closes[h]
        if macd[h+33] < -4.5 and macd[h+33] > -9.5:
            if MFI[h+14] > 15:
                if TRANGE[h+1] > 5 and TRANGE[h+1] < 10:
                    if real_atr[h + 14] > 4.5 and real_atr[h+14] < 6.5:
                        if obv[h] > 1000:
                            if current_rsi > 15:
                                if current_rsi < rsi_oversold:
                                    if in_position:
                                        print("Oversold - Already Purchased")
                                    else:
                                        print("Oversold - Purchase")
                                        # To collect data to a txt file to improve algorithm
                                        tuple_num = ("Buy - Price", "Price:", data, "MACD:", macd[h+33], "OBV:", obv[h], "RSI:", current_rsi, "TRANGE:", TRANGE[h+1], "ATR:", real_atr[h+14], "MFI:", MFI[h+14], currentTime)
                                        with open('BuySellData.txt', 'a') as f:
                                            with redirect_stdout(f):
                                                print(tuple_num)
                                        position_value.append(price_of_closes[h])
                                        rsisave.append(current_rsi)
                                        in_position = True
        # Algorithm to determine sell
        if macd[h+33] > 2:
            if TRANGE[h+1] < 6 and TRANGE[h+1] > 3.75:
                if real_atr[h+14] > 3 and real_atr[h+14] < 4:
                    if in_position:
                        if rsisave[-1] < 15:
                            rsi_overbought = 80
                        if current_rsi > rsi_overbought:
                            print("Sell- Price")
                            tuple_num = ("Sell - Price", "Price:", data, "MACD:", macd[h+33], "OBV:", obv[h], "RSI:", current_rsi, "TRANGE:", TRANGE[h+1], "ATR:", real_atr[h+14], "MFI:", MFI[h+14], currentTime)
                            with open('BuySellData.txt', 'a') as f:
                                with redirect_stdout(f):
                                    print(tuple_num)
                            in_position = False
        thing()
thing()
print("4")
