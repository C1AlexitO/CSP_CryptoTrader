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
position_value = []
h = -40
def thing(xo, yo, zo, co, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15, x16, x17, x18, x19, x20, x21):
        global in_position, candles, h, rsisave, rsi_overbought, position_value
        h = h - 1
        rsi_period = 14
        rsi_overbought = 71
        rsi_oversold = 25
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
        np_prices = numpy.array(price_of_closes[zo:])
        np_volume = numpy.array(volume_of_closes[zo:])
        np_price_high = numpy.array(price_of_highs[zo:])
        np_price_low = numpy.array(price_of_lows[zo:])
        np_price_open = numpy.array(price_of_opens[zo:])
        rsi = talib.RSI(np_prices, rsi_period)
        current_rsi = rsi[xo]

        # Using TA-Lib to get indicators to purchase or sell and printing them out to console

        macd, macdsignal, macdhist = talib.MACD(np_prices[zo:], fastperiod=12, slowperiod=26, signalperiod=9)
        obv = talib.OBV(np_prices[zo:], np_volume[zo:])
        real_atr = talib.ATR(np_price_high[h:], np_price_low[zo:], np_prices[zo:], timeperiod=14)
        AD = talib.AD(np_price_high[zo:], np_price_low[zo:], np_prices[zo:], np_volume[zo:])
        TRANGE = talib.TRANGE(np_price_high[zo:], np_price_low[zo:], np_prices[zo:])
        MFI = talib.MFI(np_price_high[zo:], np_price_low[zo:], np_prices[zo:], np_volume[zo:], timeperiod=14)
        currentTime = datetime.datetime.fromtimestamp(inttime[zo] / 1e3)
        data = price_of_closes[zo]
        if macd[co] < x13 and macd[co] > x14:
            if MFI[xo] > x15:
                if TRANGE[yo] > x16 and TRANGE[yo] < x17:
                    if real_atr[xo] > x18 and real_atr[xo] < x19:
                        if obv[zo] > x20:
                            # Change back to current_rsi > 15 if not profitable
                            if current_rsi > x21:
                                if current_rsi < rsi_oversold:
                                    if in_position:
                                        print("Oversold - Already Purchased")
                                    else:
                                        print("Oversold - Purchase")
                                        # To collect data to a txt file to improve algorithm
                                        tuple_num = ("Buy - Price", "Price:", data, "MACD:", macd[co], "OBV:", obv[zo], "RSI:", current_rsi, "TRANGE:", TRANGE[yo], "ATR:", real_atr[xo], "MFI:", MFI[xo], currentTime)
                                        with open('BuySellData.txt', 'a') as f:
                                            with redirect_stdout(f):
                                                 print(tuple_num)
                                        in_position = True
        if macd[co] > x7:
            if TRANGE[yo] < x8 and TRANGE[yo] > x9:
                if real_atr[xo] > x10 and real_atr[xo] < x11:
                    if in_position:
                        if current_rsi > x12:
                            print("SELLOOO")
                            tuple_num = ("Sell - Price", "Price:", data, "MACD:", macd[co], "OBV:", obv[zo], "RSI:", current_rsi, "TRANGE:", TRANGE[yo], "ATR:", real_atr[xo], "MFI:", MFI[xo], currentTime)
                            with open('BuySellData.txt', 'a') as f:
                                with redirect_stdout(f):
                                    print(tuple_num)
                            in_position = False

        if macd[co] > x6:
            if TRANGE[yo] < x2 and TRANGE[yo] > x3:
                if real_atr[xo] > x4 and real_atr[xo] < x5:  # maybe change 5 to 4
                    if in_position:
                        if current_rsi > rsi_overbought:
                            print("Sell- Price")
                            tuple_num = ("Sell - Price", "Price:", data, "MACD:", macd[co], "OBV:", obv[zo], "RSI:", current_rsi, "TRANGE:", TRANGE[yo], "ATR:", real_atr[xo], "MFI:", MFI[xo], currentTime)
                            with open('BuySellData.txt', 'a') as f:
                                 with redirect_stdout(f):
                                    print(tuple_num)
                            in_position = False

        thing(h+14, h+1, h, h+33, 6, 3.75, 3, 4, 2, 6, 12, 6, 6, 9, 70, -4.5, -9.5, 15, 5, 9.75, 4.5, 6.5, 1000, 10)
thing(h+14, h+1, h, h+33, 6, 3.75, 3, 4, 2, 6, 12, 6, 6, 9, 70, -4.5, -9.5, 15, 5, 9.75, 4.5, 6.5, 1000, 10)
print("4")
