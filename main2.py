print("1) ETH 2) BTC 3) BLZ 4) LIT")
input101 = int(input())
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
candles_eth = client.get_historical_klines('ETHUSDT', Client.KLINE_INTERVAL_1MINUTE, "2 days ago GMT+1")
candles_eth.reverse()
candles_btc = client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1MINUTE, "2 days ago GMT+1")
candles_btc.reverse()
candles_lit = client.get_historical_klines('LITUSDT', Client.KLINE_INTERVAL_1MINUTE, "2 days ago GMT+1")
candles_lit.reverse()
candles_blz = client.get_historical_klines('BLZUSDT', Client.KLINE_INTERVAL_1MINUTE, "2 days ago GMT+1")
candles_blz.reverse()

position_value = []
h = -40
#rsi_overbought, rsi_oversold,
def thing(rsi_overbought, rsi_oversold, candles, xo, yo, zo, co, x2, x3, x4, x5, x6, x13, x14, x15, x16, x17, x18, x19, x20, x21, x22, x23, x24):
        global in_position, h, position_value
        h = h - 1
        rsi_period = 14
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
                        if obv[zo] > x20 and obv[zo] < x23:
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
        if macd[co] > x6 and macd[co] < x24:
            if TRANGE[yo] < x2 and TRANGE[yo] > x3:
                if real_atr[xo] > x4 and real_atr[xo] < x5:  # maybe change 5 to 4
                    if obv[zo] < x22:
                        if in_position:
                            if current_rsi > rsi_overbought:
                                print("Sell- Price")
                                tuple_num = ("Sell - Price", "Price:", data, "MACD:", macd[co], "OBV:", obv[zo], "RSI:", current_rsi, "TRANGE:", TRANGE[yo], "ATR:", real_atr[xo], "MFI:", MFI[xo], currentTime)
                                with open('BuySellData.txt', 'a') as f:
                                    with redirect_stdout(f):
                                        print(tuple_num)
                                in_position = False
# 45 29
        if rsi_oversold == 29:
            thing(45, 29, candles_btc, h + 14, h + 1, h, h + 33, 110, 60, 70, 115, 35, 0, -25, 18, 0, 1000, 90, 110, 1750, 18, 1750, 2500, 50)
        if rsi_oversold == 27:
            thing(71, 27, candles_eth, h + 14, h + 1, h, h + 33, 6, 3.75, 3, 4, 2, -4.5, -9.5, 35, 5, 9.75, 4.5, 6.5, 1000, 10, 5000, 50000, 5000)
        if rsi_oversold == 28:
            thing(71, 28, candles_lit, h + 14, h + 1, h, h + 33, 0.30, 0.075, 0.10, 0.25, 0, 0.03, 0.01, 30, 0.05, 0.25, 0.06, 0.15, 145, 0, 5000, 450, 50000)
        if rsi_oversold == 28.9:
            thing(80, 28.9, candles_blz, h + 14, h + 1, h, h + 33, 100000, -100000, -100000, 100000, -1, 8, 0, 28, -100000, 100000, -100000, 100000, 80, -100000, 15, 100, 1)
if input101 == 1:
    thing(71, 27, candles_eth, h + 14, h + 1, h, h + 33, 6, 3.75, 3, 4, 2, -4.5, -9.5, 35, 5, 9.75, 4.5, 6.5, 1000, 10, 5000, 50000, 5000)
if input101 == 2:
    thing(45, 29, candles_btc, h + 14, h + 1, h, h + 33, 110, 60, 70, 115, 35, 0, -25, 18, 0, 1000, 90, 110, 2000, 18, 1750, 2500, 50)
if input101 == 3:
    thing(80, 29, candles_blz, h + 14, h + 1, h, h + 33, 100000, -100000, -100000, 100000, -1, 8, 0, 28, -100000, 100000, -100000, 100000, 80, -100000, 15, 100, 1)
if input101 == 4:
    thing(74.5, 28, candles_lit, h + 14, h + 1, h, h + 33, 0.30, 0.075, 0.10, 0.25, 0, 0.03, 0.01, 30, 0.05, 0.25, 0.06, 0.15, 145, 0, 5000, 450, 50000)
