from binance.client import Client
from binance.enums import *
import talib
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import math
import statistics as stat
from scipy.signal import savgol_filter
from openpyxl import Workbook


ext = 200
color = {
    "green": "#0ecb81",
    "red": "#f6465d",
    "cyan": "#00bcd4",
    "pink": "#a42bad",
    "purple": "#621ead",
    "yellow": "#ffec3b",
    "blue": "#0016ac",
    "black": "#161a1e",
    "lgrey": "#afb5bd",
    "dgrey": "#525252",
    "orange": "#e65100",
    "brown": "#964B00",
    "rwhite": "#FFCACA",
    "gwhite": "#CDFFCA",
    0: "#ffec3b",
    1: "#e65100",
    2: "#00bcd4",
    3: "#621ead",
    4: "#0016ac",
}

api = open("api.txt", "r")
api_key = api.readline()[:-1]
api_secret = api.readline()[:-1]
api.close()
client = Client(api_key, api_secret)


#  returns the price of the asset
def assetprice(symbol):
    trades = pd.DataFrame(client.get_recent_trades(symbol=symbol))
    trades = trades.iloc[:, 1]
    price = trades.max()
    price = float(price)
    return price


#  returns the amount of asset
def assetamount(symbol):
    balance = client.get_asset_balance(asset=symbol)
    asset = balance["free"]
    asset = float(asset)
    return asset


#  creates a lookback based on interval and length. Default length = 500
def lbgen(interval, length=500):
    n = interval[:-1]
    n = int(n)
    n = n * length
    n = str(n)
    if interval[-1] == "m":
        n = n + " minute"
    elif interval[-1] == "h":
        n = n + " hour"
    elif interval[-1] == "d":
        n = n + " day"
    return n


#  retrieves data from binance based on symbol, interval, and lookback
#  serves the data in a pandas dataframe
#  acceptable interval and lookback unit: m or minute, h or hour, d or day
#  ex: getdata('BNBUSDT', '5m', '1 hour')
def getdata(symbol, interval, lookback):
    frame = pd.DataFrame(
        client.get_historical_klines(symbol, interval, lookback + " ago UTC")
    )
    frame = frame.iloc[:, :6]
    frame.columns = ["Time", "Open", "High", "Low", "Close", "Volume"]
    frame = frame.set_index("Time")
    frame.index = pd.to_datetime(frame.index, unit="ms")
    frame = frame.astype(float)
    return frame


#  converts list into data that is acceptable by talib
def suittalib(list):
    list = [float(x) for x in list]
    list = np.array(list)
    return list


#  returns the second derivative of a data
def derivative(data, degree):
    drv = [data]
    for i in range(degree):
        drv.append([])
        for j in range(len(data)):
            if j == 0:
                drv[i + 1].append(float("nan"))
            else:
                if drv[i][j - 1] == float("nan"):
                    drv[i + 1].append(float("nan"))
                else:
                    drv[i + 1].append(drv[i][j] - drv[i][j - 1])
    return drv[degree]


def difference(frame, data1, data2):
    diff = []
    for i in range(len(frame[data1])):
        if frame[data1][i] == float("nan") or frame[data2][i] == float("nan"):
            diff.append(float("nan"))
        else:
            diff.append(frame[data1][i] - frame[data2][i])
    return diff


def deviation(frame):
    dev = []
    for i in range(len(frame)):
        if frame["BBand.Up"][i] == float("nan"):
            dev.append(float("nan"))
        else:
            stdev = (frame["BBand.Up"][i] - frame["BBand.Mid"][i]) / 2
            dev.append((frame["Close"][i] - frame["BBand.Mid"][i]) / stdev)
    return dev


#  adds indicator on the dataframe
#  indicators input: [[ind1, setting1, ..., settingn], ... , [indn, setting1, ..., settingn]]
#  lists of indicators and it's settings:
#       MA          : ['MA', length] or ['MA', length, data]
#       EMA         : ['EMA', length] or ['EMA', length, data]
#       RSI         : ['RSI', length]
#       CCI         : ['CCI', length]
#       Aroon       : ['AROON', length]
#       Stochastic  : ['STOCH', length, SmoothK, SmoothD]
#       Stoch.RSI    : ['STOCHRSI', length, SmoothK, SmoothD]
#       MACD        : ['MACD', fastlength, slowlength, signallength]
#       Boll. Bands : ['BBANDS', length, mult]
#       Deviation   : ['DEV']
#       Difference  : ['DIFF', data1, data2]
#       Reg. Slope  : ['REG', length] or ['REG', length, data]
#       Reg. Angle  : ['REGA, length] or ['REGA, length, data]
#       TS Forecast : ['TSF', length] or ['TSF', length, data]


def addind(frame, indicators=[["EMA", 5], ["EMA", 10], ["EMA", 30], ["RSI", 14]]):
    for ind in indicators:
        if ind[0] == "MA":
            if len(ind) == 2:
                frame["MA" + str(ind[1])] = talib.MA(
                    frame["Close"], timeperiod=ind[1], matype=0
                )
            elif len(ind) == 3:
                frame[ind[2] + ".MA" + str(ind[1])] = talib.MA(
                    frame[ind[2]], timeperiod=ind[1], matype=0
                )
        elif ind[0] == "EMA":
            if len(ind) == 2:
                frame["EMA" + str(ind[1])] = talib.EMA(
                    frame["Close"], timeperiod=ind[1]
                )
            elif len(ind) == 3:
                frame[ind[2] + ".EMA" + str(ind[1])] = talib.EMA(
                    frame[ind[2]], timeperiod=ind[1]
                )
        elif ind[0] == "SMA":
            if len(ind) == 2:
                frame["SMA" + str(ind[1])] = talib.SMA(
                    frame["Close"], timeperiod=ind[1]
                )
            elif len(ind) == 3:
                frame[ind[2] + ".SMA" + str(ind[1])] = talib.SMA(
                    frame[ind[2]], timeperiod=ind[1]
                )
        elif ind[0] == "RSI":
            frame["RSI"] = talib.RSI(frame["Close"], timeperiod=ind[1])
        elif ind[0] == "STOCH":
            if len(ind) == 4:
                slowk, slowd = talib.STOCH(
                    frame["High"],
                    frame["Low"],
                    frame["Close"],
                    fastk_period=ind[1],
                    slowk_period=ind[2],
                    slowk_matype=0,
                    slowd_period=ind[3],
                    slowd_matype=0,
                )
                frame["Stoch.K"] = slowk
                frame["Stoch.D"] = slowd
            elif len(ind) == 5:
                slowk, slowd = talib.STOCH(
                    frame["High"],
                    frame["Low"],
                    frame["Close"],
                    fastk_period=ind[1],
                    slowk_period=ind[2],
                    slowk_matype=0,
                    slowd_period=ind[3],
                    slowd_matype=0,
                )
                frame["Stoch.K" + ind[4]] = slowk
                frame["Stoch.D" + ind[4]] = slowd
        elif ind[0] == "STOCH.RSI":
            fastk, fastd = talib.STOCHRSI(
                frame["RSI"],
                timeperiod=ind[1],
                fastk_period=ind[2],
                fastd_period=ind[3],
                fastd_matype=0,
            )
            frame["Stoch.RSI.K"] = fastk
            frame["Stoch.RSI.D"] = fastd
        elif ind[0] == "MACD":
            macd, macdsignal, macdhist = talib.MACD(
                frame["Close"],
                fastperiod=ind[1],
                slowperiod=ind[2],
                signalperiod=ind[3],
            )
            frame["MACD"] = macd
            frame["MACD.Sign"] = macdsignal
            frame["MACD.Hist"] = macdhist
        elif ind[0] == "BBANDS":
            upperband, middleband, lowerband = talib.BBANDS(
                frame["Close"],
                timeperiod=ind[1],
                nbdevup=ind[2],
                nbdevdn=ind[2],
                matype=0,
            )
            frame["BBand.Up"] = upperband
            frame["BBand.Mid"] = middleband
            frame["BBand.Low"] = lowerband
        elif ind[0] == "DEV":
            frame["Deviation"] = deviation(frame)
        elif ind[0] == "DIFF":
            frame[ind[1] + str("-") + ind[2]] = difference(frame, ind[1], ind[2])
        elif ind[0] == "CCI":
            frame["CCI"] = talib.CCI(
                frame["High"], frame["Low"], frame["Close"], timeperiod=ind[1]
            )
        elif ind[0] == "AROON":
            aroondown, aroonup = talib.AROON(
                frame["High"], frame["Low"], timeperiod=ind[1]
            )
            frame["AROON.Down"] = aroondown
            frame["AROON.Up"] = aroonup
        elif ind[0] == "REG":
            if len(ind) == 2:
                frame["REG"] = talib.LINEARREG_SLOPE(frame["Close"], timeperiod=ind[1])
            elif len(ind) == 3:
                frame[str(ind[2]) + ".REG"] = talib.LINEARREG_SLOPE(
                    frame[ind[2]], timeperiod=ind[1]
                )
        elif ind[0] == "REGA":
            if len(ind) == 2:
                frame["REGA"] = talib.LINEARREG_ANGLE(frame["Close"], timeperiod=ind[1])
            elif len(ind) == 3:
                frame[str(ind[2]) + ".REGA"] = talib.LINEARREG_ANGLE(
                    frame[ind[2]], timeperiod=ind[1]
                )

        elif ind[0] == "TSF":
            if len(ind) == 2:
                frame["TSF" + str(ind[1])] = talib.TSF(
                    frame["Close"], timeperiod=ind[1]
                )
            elif len(ind) == 3:
                frame[str(ind[2]) + ".TSF" + str(ind[1])] = talib.TSF(
                    frame[ind[2]], timeperiod=ind[1]
                )
    return frame


#  creates a dataframe without empty value indicators
def getcleanind(
    symbol,
    interval,
    lookback,
    indicators=[["EMA", 5], ["EMA", 10], ["EMA", 30], ["RSI", 14]],
):
    frame = getdata(symbol, interval, lookback)
    tail = len(frame)
    nlook = lookback[: lookback.index(" ")]
    nlook = int(nlook)
    nint = interval[:-1]
    nint = int(nint)
    time = lookback[(lookback.index(" ") + 1) :]
    if interval[-1] == "m":
        if time == "minute":
            lookback = None
            lookback = (math.floor(nlook / nint) + 250) * nint
        elif time == "hour":
            lookback = None
            lookback = (math.floor(60 * nlook / nint) + 250) * nint
        elif time == "day":
            lookback = None
            lookback = (math.floor(1440 * nlook / nint) + 250) * nint
        lookback = str(lookback) + " minute"
    elif interval[-1] == "h":
        if time == "hour":
            lookback = None
            lookback = (math.floor(nlook / nint) + 250) * nint
        elif time == "day":
            lookback = None
            lookback = (math.floor(24 * nlook / nint) + 250) * nint
        lookback = str(lookback) + " hour"
    frame = getdata(symbol, interval, lookback)
    addind(frame, indicators)
    frame = frame.tail(tail)
    return frame


#  returns the corresponding length for second interval based on the first interval
def corrlen(int1, int2, length):
    if int1[-1] == "m":
        tint1 = int(int1[:-1])
    elif int1[-1] == "h":
        tint1 = int(int1[:-1]) * 60
    elif int1[-1] == "d":
        tint1 = int(int1[:-1]) * 1440
    else:
        return None
    if int2[-1] == "m":
        tint2 = int(int2[:-1])
    elif int2[-1] == "h":
        tint2 = int(int2[:-1]) * 60
    elif int2[-1] == "d":
        tint2 = int(int2[:-1]) * 1440
    else:
        return None
    return math.ceil(tint1 / tint2 * length)


#  returns the corresponding time based on the interval used
def corrtime(interval, curtime):
    if interval == "5m":
        for i in range(2):
            if 5 * i <= int(curtime[14:16]) < 5 * (i + 1):
                corrtime = curtime[0:14] + "0" + str(5 * i) + ":00"
        for i in range(2, 12):
            if 5 * i <= int(curtime[14:16]) < 5 * (i + 1):
                corrtime = curtime[0:14] + str(5 * i) + ":00"
    elif interval == "15m":
        for i in range(4):
            if 15 * i <= int(curtime[14:16]) < 15 * (i + 1):
                corrtime = curtime[0:14] + str(15 * i) + ":00"
    elif interval == "30m":
        if 0 <= int(curtime[14:16]) < 30:
            corrtime = curtime[0:14] + "00:00"
        else:
            corrtime = curtime[0:14] + "30:00"
    elif interval == "1h":
        corrtime = curtime[0:14] + "00:00"
    elif interval == "2h":
        for i in range(5):
            if 2 * i <= int(curtime[11:13]) < 2 * (i + 1):
                corrtime = curtime[0:11] + "0" + str(2 * i) + ":00:00"
        for i in range(5, 12):
            if 2 * i <= int(curtime[11:13]) < 2 * (i + 1):
                corrtime = curtime[0:11] + str(2 * i) + ":00:00"
    elif interval == "4h":
        for i in range(3):
            if 4 * i <= int(curtime[11:13]) < 4 * (i + 1):
                corrtime = curtime[0:11] + "0" + str(4 * i) + ":00:00"
        for i in range(3, 6):
            if 4 * i <= int(curtime[11:13]) < 4 * (i + 1):
                corrtime = curtime[0:11] + str(4 * i) + ":00:00"
    elif interval == "6h":
        for i in range(2):
            if 6 * i <= int(curtime[11:13]) < 6 * (i + 1):
                corrtime = curtime[0:11] + "0" + str(6 * i) + ":00:00"
        for i in range(2, 4):
            if 6 * i <= int(curtime[11:13]) < 6 * (i + 1):
                corrtime = curtime[0:11] + str(6 * i) + ":00:00"
    elif interval == "8h":
        for i in range(2):
            if 8 * i <= int(curtime[11:13]) < 8 * (i + 1):
                corrtime = curtime[0:11] + "0" + str(8 * i) + ":00:00"
        for i in range(2, 3):
            if 8 * i <= int(curtime[11:13]) < 8 * (i + 1):
                corrtime = curtime[0:11] + str(8 * i) + ":00:00"
    elif interval == "12h":
        if 0 <= int(curtime[11:13]) < 12:
            corrtime = curtime[0:11] + "00:00:00"
        else:
            corrtime = curtime[0:11] + "12:00:00"
    return corrtime


#  creates a smooth version of a data
#  winlen must be odd integer with minimum value 5
#  dref is the data you want to smooth from the dataframe
def smoothdata(frame, dref, winlen=25, weight=3, n=1, label=""):
    data = frame[dref]
    for i in range(n):
        data = savgol_filter(data, winlen, weight)
    if n == 1:
        frame[dref + ".Smoothed" + label] = data
    else:
        frame[dref + ".Smoothed" + str(n) + label] = data


#  determines the position of a data compared to another data using t-test
#  min rg is 3 while max rg is 10
#  returns ['below' 'equal' or 'above', t value]
def comparedata(data1, data2=[], altdata="", rg=5, con=95):
    ttable95 = {
        4: 2.776,
        6: 2.447,
        8: 2.306,
        10: 2.228,
        12: 2.179,
        14: 2.145,
        16: 2.120,
        18: 2.101,
    }

    ttable98 = {
        4: 3.747,
        6: 3.143,
        8: 2.896,
        10: 2.764,
        12: 2.681,
        14: 2.624,
        16: 2.583,
        18: 2.552,
    }

    ttable99 = {
        4: 4.604,
        6: 3.707,
        8: 3.355,
        10: 3.169,
        12: 3.055,
        14: 2.977,
        16: 2.921,
        18: 2.878,
    }
    if altdata == "":
        if len(data1) < rg + 1 or len(data2) < rg + 1:
            return "-"
        else:
            xbf = stat.mean(data1[-rg - 1 : -1])
            xbi = stat.mean(data2[-rg - 1 : -1])
            sdf = stat.stdev(data1[-rg - 1 : -1])
            sdi = stat.stdev(data2[-rg - 1 : -1])
            sdp = math.sqrt(0.5 * (sdf**2 + sdi**2))
            t = (xbf - xbi) / sdp / (2 / rg)
    else:
        if len(data1) < rg + 1:
            return "-"
        else:
            xbf = stat.mean(data1[-rg - 1 : -1])
            xbi = altdata
            sdf = stat.stdev(data1[-rg - 1 : -1])
            sdi = 0
            sdp = math.sqrt(0.5 * (sdf**2 + sdi**2))
            t = (xbf - xbi) / sdp / (2 / rg)

    trend = ""
    if con == 95:
        if t < -ttable95[2 * rg - 2]:
            trend = "below"
        elif t > ttable95[2 * rg - 2]:
            trend = "above"
        else:
            trend = "equal"
    elif con == 98:
        if t < -ttable98[2 * rg - 2]:
            trend = "below"
        elif t > ttable98[2 * rg - 2]:
            trend = "above"
        else:
            trend = "equal"
    elif con == 99:
        if t < -ttable99[2 * rg - 2]:
            trend = "below"
        elif t > ttable99[2 * rg - 2]:
            trend = "above"
        else:
            trend = "equal"

    return [trend, t]


#  checks the latests interval whether it is valley or peak
#  extreme value: 'low' or 'high'
#  rad is the radius of comparison
#  rg is the value which the data must be in range of [min, max]
#  mindifr is the minimum ratio of the left side difference with the right side difference
#  returns [time, valley or peak value] or []
def dataxtr(data, extreme, rad=2, rg=["", ""], mindifr=0):
    xtr = []
    if extreme == "low" and len(data) >= (2 * rad + 2):
        x = True
        ldif = 0
        rdif = 0
        for i in range(1, rad + 1):
            if data[-rad - 2] >= min(data[-rad - 2 - i], data[-rad - 2 + i]):
                x = False
            if data[-rad - 2 - i] - data[-rad - 2] > ldif:
                ldif = data[-rad - 2 - i] - data[-rad - 2]
            if data[-rad - 2 + i] - data[-rad - 2] > rdif:
                rdif = data[-rad - 2 + i] - data[-rad - 2]
        if min(ldif, rdif) < mindifr * max(ldif, rdif):
            x = False
        if rg[0] != "":
            if data[-rad - 2] < rg[0]:
                x = False
        if rg[1] != "":
            if data[-rad - 2] > rg[1]:
                x = False
        if x == True:
            xtr.append(data.index[-rad - 2])
            xtr.append(data[-rad - 2])
    elif extreme == "high" and len(data) >= (2 * rad + 2):
        x = True
        ldif = 0
        rdif = 0
        for i in range(1, rad + 1):
            if data[-rad - 2] <= max(data[-rad - 2 - i], data[-rad - 2 + i]):
                x = False
            if data[-rad - 2] - data[-rad - 2 - i] > ldif:
                ldif = data[-rad - 2] - data[-rad - 2 - i]
            if data[-rad - 2] - data[-rad - 2 + i] < rdif:
                rdif = data[-rad - 2] - data[-rad - 2 + i]
        if min(ldif, rdif) < mindifr * max(ldif, rdif):
            x = False
        if rg[0] != "":
            if data[-rad - 2] < rg[0]:
                x = False
        if rg[1] != "":
            if data[-rad - 2] > rg[1]:
                x = False
        if x == True:
            xtr.append(data.index[-rad - 2])
            xtr.append(data[-rad - 2])
    return xtr


#  searches for the latest value extreme after ignoring the current interval
def prevdataxtr(data, extreme, rad=2, rg=["", ""], nlimit=0, mindifr=0):
    data = data[:-1]
    xtr = []
    if nlimit != 0:
        i = 0
        while xtr == [] and len(data) >= (2 * rad + 2) and i < nlimit:
            xtr = dataxtr(data, extreme, rad, rg, mindifr)
            data = data[:-1]
            i = i + 1
    else:
        while xtr == [] and len(data) >= (2 * rad + 2):
            xtr = dataxtr(data, extreme, rad, rg, mindifr)
            data = data[:-1]
    return xtr


#  creates a list containing all value extremes
#  results: [[time], [value]] or [[time], [value], i] with i is the number of intervals if max > 0
def alldataxtr(data, extreme, rad=2, rg=["", ""], mindifr=0, max=0):
    xtr = [[], []]
    if max == 0:
        while len(data) >= (2 * rad + 2):
            if dataxtr(data, extreme, rad, rg, mindifr) != []:
                xtr[0].append(dataxtr(data, extreme, rad, rg, mindifr)[0])
                xtr[1].append(dataxtr(data, extreme, rad, rg, mindifr)[1])
            data = data[:-1]
        return xtr
    else:
        i = 0
        while len(data) >= (2 * rad + 2) and len(xtr[0]) < max:
            if dataxtr(data, extreme, rad, rg, mindifr) != []:
                xtr[0].append(dataxtr(data, extreme, rad, rg, mindifr)[0])
                xtr[1].append(dataxtr(data, extreme, rad, rg, mindifr)[1])
            i = i + 1
            data = data[:-1]
        xtr.append(i)
        return xtr


#  returns information on cross of two indicators between the range determined
#  may also returns information on other data
#  ex: data = ['Close', 'RSI', 'MACD']
#  filling in direction with 'up' or 'down' will only show the appropriate cross with the same movement
#  rg = [minimum value, maximum value]
#  if cross it will return [direction, crossvalue, time, ind1...] else ['no']
def indx(frame, dref1, dref2, direction="", rg=["", ""], data=[]):
    indx = ["no"]
    cross = False
    dir = "no"
    a = frame[dref1][-3]
    b = frame[dref1][-2]
    c = frame[dref2][-3]
    d = frame[dref2][-2]
    if a < c and b >= d:
        cross = True
        dir = "up"
    elif a > c and b <= d:
        cross = True
        dir = "down"
    if direction != "" and direction != dir:
        cross = False
    if cross:
        x = (b - a) * (a - c) / (a - b - c + d) + a
        valid = True
        if rg[0] != "":
            if x < rg[0]:
                valid = False
        if rg[1] != "":
            if x > rg[1]:
                valid = False
        if valid:
            indx = [dir]
            indx.append(x)
            indx.append(frame.index[-2])
            for info in data:
                indx.append(frame[info][-2])
    return indx


#  finds the previous stochastic cross
#  if ign=True, automatically ignores the current time frame
def previndx(
    frame, dref1, dref2, direction="", rg=["", ""], data=[], max=200, ign=True
):
    if ign:
        frame = frame[:-1]
    i = 1
    while (i <= max or len(frame) >= 3) and indx(
        frame, dref1, dref2, direction, rg, data
    ) == ["no"]:
        frame = frame[:-1]
        i = i + 1

    if i > max or len(frame) < 3:
        return ["no"]
    else:
        return indx(frame, dref1, dref2, direction, rg, data)


# returns strong uptrend, weak uptrend, sideways, weak downtrend, or strong downtrend
def st2trend(frame):
    if (
        comparedata(frame["Close"], frame["EMA200"])[0] == "above"
        and frame["EMA50"][-2] > frame["EMA100"][-2] > frame["EMA200"][-2]
        and frame["EMA50"][-3] > frame["EMA100"][-3] > frame["EMA200"][-3]
        and frame["EMA50"][-4] > frame["EMA100"][-4] > frame["EMA200"][-4]
        and (
            comparedata(frame["Close"], frame["EMA100"])[0] == "above"
            or comparedata(frame["RSI"], altdata=50)[0] == "above"
        )
    ):
        trend = "uptrend"
    elif (
        comparedata(frame["Close"], frame["EMA200"])[0] == "below"
        and frame["EMA50"][-2] < frame["EMA100"][-2] < frame["EMA200"][-2]
        and frame["EMA50"][-3] < frame["EMA100"][-3] < frame["EMA200"][-3]
        and frame["EMA50"][-4] < frame["EMA100"][-4] < frame["EMA200"][-4]
        and (
            comparedata(frame["Close"], frame["EMA100"])[0] == "below"
            or comparedata(frame["RSI"], altdata=50)[0] == "below"
        )
    ):
        trend = "downtrend"
    else:
        trend = "uncertain"

    return trend


def bhreturn(frame, int):
    pairprice = []
    ret = []
    for i in range(len(frame) // int):
        buy = frame["Open"][i * int]
        sell = frame["Close"][i * int + int - 1]
        pairprice.append([buy, sell])
        ret.append(sell / buy)

    avg = stat.geometric_mean(ret)
    std = stat.stdev(ret)

    return (pairprice, ret, avg, std)
