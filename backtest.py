from library import *


#  BACKTEST SCHEME
#  A strategy is defined, specifically made for backtesting
#  Meanwhile, a tester is created to run the strategy
#  The tester will loop the strategy which will execute it as many times as the length,
#  one by one from the oldest data to the latest one
#  An array called trade is used to carry the state of the latest trade
#  When the tester is first started, trade = ['No Trade']
#  When the criteria for buying is met, the trade array will receive the following information:
#  trade = ['Bought!', [criteria, buying time, buying price, cutloss, others..]]
#  The time and buying price will then be recorded into the tradehis array into the following format:
#  [[criteria, buying time 1, buying price 1], ...]
#  Also change the trade array into trade:
#  ['Hold', [criteria, buying time, buying price, cutloss, others..]]
#  When the criteria for selling is met, the trade array will receive the following information:
#  trade = ['Sold!', [criteria, buying time, buying price, cutloss, others..], [selling time, selling price]]
#  The time and selling price will then be recorded into the tradehis array and immediately
#  change the trade array into trade = ['No Trade']
#  The format of information in tradehis will be as follow:
#  [[criteria, buying time 1, buying price 1, selling time 1, selling price 1], ...]
#  traderecap will then show important information of the trade as a whole
#  Showing the candlestick chart along with the indicators as well as trade is optional


def strat2test(frames, index, trade, intervals=["1h"], rad=2):
    frame1 = frames[0].iloc[(index - ext) : index]
    #  Buying
    if trade[0] == "No Trade":
        #  During Downtrend
        if st2trend(frame1) == "downtrend":
            curstoch = indx(
                frame1, "Stoch.K", "Stoch.D", direction="up", rg=["", 20], data=["MACD"]
            )
            prevstoch = previndx(
                frame1,
                "Stoch.K",
                "Stoch.D",
                direction="up",
                rg=["", 20],
                data=["MACD"],
                max=50,
            )
            position = comparedata(frame1["RSI"], altdata=30, rg=7, con=99)
            if curstoch != ["no"] and prevstoch != ["no"]:
                if (
                    curstoch[3] > prevstoch[3]
                    and position[0] == "above"
                    and frame1["RSI"][-2] > frame1["RSI"][-3]
                ):
                    trade[0] = "Bought!"
                    trade.append(["A1"])  # Criteria
                    trade[1].append(frame1.index[-1])  # Buying Time
                    trade[1].append(frame1["Open"][-1])  # Buying Price
                    trade[1].append(frame1["Close"][-3])  # Cutloss
                    trade[1].append(curstoch[1])  # Stoch value
                    return trade

            # curreg = indx(frame1, 'REG', 'REG.SMA3', direction='up')
            # position1 = comparedata(frame1['RSI'], frame1['RSI.SMA30'], rg=7, con=95)
            # position2 = comparedata(frame1['RSI'], frame1['RSI.SMA50'], rg=7, con=95)
            # position3 = comparedata(frame1['RSI'], altdata=50, rg=7, con=99)
            # if (position1[0] == 'above' or position2[0] == 'above' or position3[0] == 'above') and curreg[0] == 'up':
            #     trade[0] = 'Bought!'
            #     trade.append(['A2'])  # Criteria
            #     trade[1].append(frame1.index[-1])  # Buying Time
            #     trade[1].append(frame1['Open'][-1])  # Buying Price
            #     trade[1].append(min(frame1['Close'][-5:-2]))  # Cutloss
            #     return trade

        #  During Uncertainty
        elif st2trend(frame1) == "uncertain":
            if frame1["Close"][-2] < frame1["EMA75"][-2]:
                curreg = indx(frame1, "REG", "REG.SMA3", direction="up")
                position1 = comparedata(
                    frame1["RSI"], frame1["RSI.SMA30"], rg=5, con=95
                )
                position2 = comparedata(
                    frame1["RSI"], frame1["RSI.SMA50"], rg=5, con=95
                )
                if curreg[0] == "up" and (
                    position1[0] == "above" or position2[0] == "above"
                ):
                    trade[0] = "Bought!"
                    trade.append(["B1"])  # Criteria
                    trade[1].append(frame1.index[-1])  # Buying Time
                    trade[1].append(frame1["Open"][-1])  # Buying Price
                    trade[1].append(min(frame1["Close"][-5:-2]))  # Cutloss
                    return trade
            else:
                curreg = indx(frame1, "REG", "REG.SMA3", direction="up")
                position1 = comparedata(
                    frame1["RSI"], frame1["RSI.SMA30"], rg=5, con=95
                )
                position2 = comparedata(
                    frame1["RSI"], frame1["RSI.SMA50"], rg=5, con=95
                )
                if curreg[0] == "up" and (
                    position1[0] == "above" or position2[0] == "above"
                ):
                    trade[0] = "Bought!"
                    trade.append(["B2"])  # Criteria
                    trade[1].append(frame1.index[-1])  # Buying Time
                    trade[1].append(frame1["Open"][-1])  # Buying Price
                    trade[1].append(min(frame1["Close"][-5:-2]))  # Cutloss
                    return trade

        #  During Uptrend
        elif st2trend(frame1) == "uptrend":
            curmacd = indx(frame1, "MACD", "MACD.Sign", direction="up")
            position1 = comparedata(frame1["RSI"], frame1["RSI.SMA30"], rg=5, con=95)
            position2 = comparedata(frame1["RSI"], frame1["RSI.SMA50"], rg=5, con=95)
            if curmacd[0] == "up" and (
                position1[0] == "above" or position2[0] == "above"
            ):
                trade[0] = "Bought!"
                trade.append(["C1"])  # Criteria
                trade[1].append(frame1.index[-1])  # Buying Time
                trade[1].append(frame1["Open"][-1])  # Buying Price
                trade[1].append(min(frame1["Close"][-5:-2]))  # Cutloss
                return trade

    #  Selling
    if trade[0] == "Hold":
        #  Cutloss
        if frame1["Low"][-1] < trade[1][3] and trade[1][0] != "A1":
            trade[0] = "Sold!"
            trade.append([frame1.index[-1]])
            trade[2].append(trade[1][3])
            return trade
        if trade[1][0] == "A1":
            if frame1["Low"][-1] < trade[1][3] and frame1["RSI"][-2] < 30:
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(trade[1][3])
                return trade
            if frame1["Stoch.K"][-2] < trade[1][4]:
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(frame1["Open"][-1])
                return trade

        #  During Downtrend
        if st2trend(frame1) == "downtrend":
            curstoch = indx(frame1, "Stoch.K", "Stoch.D", direction="down")
            prevstoch = previndx(frame1, "Stoch.K", "Stoch.D", direction="down")
            if curstoch[0] == "down" and curstoch[1] >= 80:
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(frame1["Open"][-1])
                return trade
            if (
                curstoch[0] == "down"
                and curstoch[1] < prevstoch[1]
                and prevstoch[2] > trade[1][1]
            ):
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(frame1["Open"][-1])
                return trade

        #  During Uncertainty
        elif st2trend(frame1) == "uncertain":
            curreg = indx(frame1, "REG", "REG.SMA3", direction="down")
            if curreg[0] == "down" and frame1["Stoch.K"][-2] > 80:
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(frame1["Open"][-1])
                return trade

            curstoch = indx(frame1, "Stoch.K", "Stoch.D", direction="down")
            prevstoch = previndx(frame1, "Stoch.K", "Stoch.D", direction="down")
            if (
                curstoch[0] == "down"
                and curstoch[1] < prevstoch[1]
                and prevstoch[2] > trade[1][1]
            ):
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(frame1["Open"][-1])
                return trade

        #  During Uptrend
        elif st2trend(frame1) == "uptrend":
            curreg = indx(frame1, "REG", "REG.SMA3", direction="down")
            if curreg[0] == "down":
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(frame1["Open"][-1])
                return trade

    return trade


def strat3test(frames, index, trade, intervals=["1h"], rad=2):
    frame1 = frames[0].iloc[(index - ext) : index]
    #  Buying
    if trade[0] == "No Trade":
        #  During Downtrend
        if st2trend(frame1) == "downtrend":
            curstoch = indx(
                frame1, "Stoch.K", "Stoch.D", direction="up", rg=["", 20], data=["MACD"]
            )
            prevstoch = previndx(
                frame1,
                "Stoch.K",
                "Stoch.D",
                direction="up",
                rg=["", 20],
                data=["MACD"],
                max=50,
            )
            position = comparedata(frame1["RSI"], altdata=30, rg=7, con=99)
            if curstoch != ["no"] and prevstoch != ["no"]:
                if (
                    curstoch[3] > prevstoch[3]
                    and position[0] == "above"
                    and frame1["RSI"][-2] > frame1["RSI"][-3]
                ):
                    trade[0] = "Bought!"
                    trade.append(["A1"])  # Criteria
                    trade[1].append(frame1.index[-1])  # Buying Time
                    trade[1].append(frame1["Open"][-1])  # Buying Price
                    trade[1].append(frame1["Close"][-3])  # Cutloss
                    trade[1].append(curstoch[1])  # Stoch value
                    return trade

            curreg = indx(frame1, "REG", "REG.SMA3", direction="up")
            position1 = comparedata(frame1["RSI"], frame1["RSI.SMA30"], rg=7, con=95)
            position2 = comparedata(frame1["RSI"], frame1["RSI.SMA50"], rg=7, con=95)
            position3 = comparedata(frame1["RSI"], altdata=50, rg=7, con=99)
            if (
                position1[0] == "above"
                or position2[0] == "above"
                or position3[0] == "above"
            ) and curreg[0] == "up":
                trade[0] = "Bought!"
                trade.append(["A2"])  # Criteria
                trade[1].append(frame1.index[-1])  # Buying Time
                trade[1].append(frame1["Open"][-1])  # Buying Price
                trade[1].append(min(frame1["Close"][-5:-2]))  # Cutloss
                return trade

        #  During Uncertainty
        elif st2trend(frame1) == "uncertain":
            if frame1["EMA75"][-2] > 0:
                curreg = indx(frame1, "REG", "REG.SMA3", direction="up")
                position1 = comparedata(
                    frame1["RSI"], frame1["RSI.SMA30"], rg=5, con=95
                )
                position2 = comparedata(
                    frame1["RSI"], frame1["RSI.SMA50"], rg=5, con=95
                )
                if curreg[0] == "up" and (
                    position1[0] == "above" or position2[0] == "above"
                ):
                    trade[0] = "Bought!"
                    trade.append(["B1"])  # Criteria
                    trade[1].append(frame1.index[-1])  # Buying Time
                    trade[1].append(frame1["Open"][-1])  # Buying Price
                    trade[1].append(min(frame1["Close"][-5:-2]))  # Cutloss
                    return trade

        #  During Uptrend
        elif st2trend(frame1) == "uptrend":
            curtsf = indx(
                frame1, "RSI.TSF14", "RSI.TSF14.MA3", direction="up", rg=[50, ""]
            )
            if curtsf[0] == "up" and frame1["RSI.TSF14.REG"][-2] > 0:
                trade[0] = "Bought!"
                trade.append(["C1"])  # Criteria
                trade[1].append(frame1.index[-1])  # Buying Time
                trade[1].append(frame1["Open"][-1])  # Buying Price
                trade[1].append(min(frame1["Close"][-5:-2]))  # Cutloss
                return trade

    #  Selling
    if trade[0] == "Hold":
        #  Cutloss
        if frame1["Close"][-1] < trade[1][3] and trade[1][0] != "A1":
            trade[0] = "Sold!"
            trade.append([frame1.index[-1]])
            trade[2].append(trade[1][3])
            return trade
        if trade[1][0] == "A1":
            if frame1["Close"][-1] < trade[1][3] and frame1["RSI"][-2] < 30:
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(trade[1][3])
                return trade
            if frame1["Stoch.K"][-2] < trade[1][4]:
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(frame1["Open"][-1])
                return trade

        #  During Downtrend
        if st2trend(frame1) == "downtrend":
            curstoch = indx(frame1, "Stoch.K", "Stoch.D", direction="down")
            prevstoch = previndx(frame1, "Stoch.K", "Stoch.D", direction="down")
            if curstoch[0] == "down" and curstoch[1] >= 80:
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(frame1["Open"][-1])
                return trade
            if (
                curstoch[0] == "down"
                and curstoch[1] < prevstoch[1]
                and prevstoch[2] > trade[1][1]
            ):
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(frame1["Open"][-1])
                return trade

        #  During Uncertainty
        elif st2trend(frame1) == "uncertain":
            curreg = indx(frame1, "REG", "REG.SMA3", direction="down")
            if curreg[0] == "down" and frame1["Stoch.K"][-2] > 80:
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(frame1["Open"][-1])
                return trade

            curstoch = indx(frame1, "Stoch.K", "Stoch.D", direction="down")
            prevstoch = previndx(frame1, "Stoch.K", "Stoch.D", direction="down")
            if (
                curstoch[0] == "down"
                and curstoch[1] < prevstoch[1]
                and prevstoch[2] > trade[1][1]
            ):
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(frame1["Open"][-1])
                return trade

        #  During Uptrend
        elif st2trend(frame1) == "uptrend":
            curtsf = indx(frame1, "RSI.TSF14", "RSI.TSF14.MA3", direction="down")
            if curtsf[0] == "down":
                trade[0] = "Sold!"
                trade.append([frame1.index[-1]])
                trade[2].append(frame1["Open"][-1])
                return trade

    return trade


indicators = {
    strat2test: [
        ["EMA", 50],
        ["EMA", 75],
        ["EMA", 100],
        ["EMA", 200],
        ["RSI", 14],
        ["SMA", 30, "RSI"],
        ["SMA", 50, "RSI"],
        ["STOCH", 14, 3, 3],
        ["MACD", 12, 26, 7],
        ["REG", 14],
        ["SMA", 3, "REG"],
        ["TSF", 14, "RSI"],
        ["REG", 30, "RSI.TSF14"],
    ],
    strat3test: [
        ["EMA", 50],
        ["EMA", 75],
        ["EMA", 100],
        ["EMA", 200],
        ["RSI", 14],
        ["SMA", 30, "RSI"],
        ["SMA", 50, "RSI"],
        ["STOCH", 14, 3, 3],
        ["MACD", 12, 26, 7],
        ["REG", 14],
        ["SMA", 3, "REG"],
        ["TSF", 14, "RSI"],
        ["MA", 3, "RSI.TSF14"],
        ["REG", 30, "RSI.TSF14"],
    ],
}


# tests the strategy for backtesting
# variable intervals must be an array
# variable strat is the strategy funtion which will be tested
# cut is used to remove a certain number of the latest intervals
def tester(symbol, intervals, length, strat, cut=0):
    frames = []
    for i in range(len(intervals)):
        lb = corrlen(intervals[0], intervals[i], length) + ext
        lookback = lbgen(intervals[i], lb)
        frames.append(getcleanind(symbol, intervals[i], lookback, indicators[strat]))
    if cut != 0:
        frames[0] = frames[0].iloc[:-cut]
    trade = ["No Trade"]
    i = 0
    tradehis = []
    for index in range(ext, length + ext - cut):
        trade = strat(frames, index, trade, intervals)
        if trade[0] == "Bought!":
            tradehis.append([trade[1][0]])
            tradehis[i].append(trade[1][1])
            tradehis[i].append(trade[1][2])
            trade[0] = "Hold"
        elif trade[0] == "Sold!":
            tradehis[i].append(trade[2][0])
            tradehis[i].append(trade[2][1])
            i = i + 1
            trade = ["No Trade"]
    return tradehis


def tradesum(tradehis, crit=False, lvg=1):
    if len(tradehis) == 0:
        print("NO TRADE OCCURED")
    else:
        if len(tradehis[-1]) == 3:
            del tradehis[-1]
        profit = 1.000
        win = 0
        loss = 0
        conswin = [0, 0]
        consloss = [0, 0]
        bigwin = 1.000
        bigloss = 1.000
        for i in range(len(tradehis)):
            curprof = (((tradehis[i][4] / tradehis[i][2] * 0.998) - 1) * lvg) + 1
            profit = profit * curprof
            if curprof >= 1:
                win = win + 1
                if curprof > bigwin:
                    bigwin = curprof
                conswin[0] = conswin[0] + 1
                if conswin[0] > conswin[1]:
                    conswin[1] = conswin[0]
                consloss[0] = 0
            else:
                loss = loss + 1
                if curprof < bigloss:
                    bigloss = curprof
                consloss[0] = consloss[0] + 1
                if consloss[0] > consloss[1]:
                    consloss[1] = consloss[0]
                conswin[0] = 0
        profit = (profit - 1) * 100
        profit = str(profit)
        bigwin = (bigwin - 1) * 100
        bigwin = str(bigwin)
        bigloss = (bigloss - 1) * 100
        bigloss = str(bigloss)
        winpct = win / (win + loss) * 100
        winpct = str(winpct)

        print("BACKTEST TRADING RECAP:")
        print("Profit/Loss  : " + profit[: profit.index(".") + 3] + "%")
        print("Total Win    : " + str(win))
        print("Total Loss   : " + str(loss))
        print("Biggest Win  : " + bigwin[: bigwin.index(".") + 3] + "%")
        print("Biggest Loss : " + bigloss[: bigloss.index(".") + 3] + "%")
        print("Win Percentage : " + winpct[: winpct.index(".") + 3] + "%")
        print("Most Consecutive Wins: " + str(conswin[1]))
        print("Most Consecutive loss: " + str(consloss[1]))
        print("")

    if crit:
        if len(tradehis) == 0:
            print("NO TRADE OCCURED")
        else:
            if len(tradehis[-1]) == 3:
                del tradehis[-1]
            ucrit = []
            for trade in tradehis:
                unique = True
                for crit in ucrit:
                    if trade[0] == crit:
                        unique = False
                if unique == True:
                    ucrit.append(trade[0])
            ucrit.sort()
            if len(ucrit) == 1:
                print("ONLY CRITERIA " + ucrit[0] + " USED!")
            else:
                for crit in ucrit:
                    profit = 1.000
                    win = 0
                    loss = 0
                    conswin = [0, 0]
                    consloss = [0, 0]
                    bigwin = 1.000
                    bigloss = 1.000
                    latesttrade = None
                    for i in range(len(tradehis)):
                        if crit == tradehis[i][0]:
                            curprof = (
                                ((tradehis[i][4] / tradehis[i][2] * 0.998) - 1) * lvg
                            ) + 1
                            profit = profit * curprof
                            if curprof >= 1:
                                win = win + 1
                                if curprof > bigwin:
                                    bigwin = curprof
                                conswin[0] = conswin[0] + 1
                                if conswin[0] > conswin[1]:
                                    conswin[1] = conswin[0]
                                consloss[0] = 0
                            else:
                                loss = loss + 1
                                if curprof < bigloss:
                                    bigloss = curprof
                                consloss[0] = consloss[0] + 1
                                if consloss[0] > consloss[1]:
                                    consloss[1] = consloss[0]
                                conswin[0] = 0
                    profit = (profit - 1) * 100
                    profit = str(profit)
                    bigwin = (bigwin - 1) * 100
                    bigwin = str(bigwin)
                    bigloss = (bigloss - 1) * 100
                    bigloss = str(bigloss)
                    winpct = win / (win + loss) * 100
                    winpct = str(winpct)

                    print("BACKTEST TRADING RECAP CRITERIA " + crit + ":")
                    print("Profit/Loss  : " + profit[: profit.index(".") + 3] + "%")
                    print("Total Win    : " + str(win))
                    print("Total Loss   : " + str(loss))
                    print("Biggest Win  : " + bigwin[: bigwin.index(".") + 3] + "%")
                    print("Biggest Loss : " + bigloss[: bigloss.index(".") + 3] + "%")
                    print("Win Percentage : " + winpct[: winpct.index(".") + 3] + "%")
                    print("Most Consecutive Wins: " + str(conswin[1]))
                    print("Most Consecutive loss: " + str(consloss[1]))
                    print("")
    return


#  plot a candlestick frame
def candlestick(frame, ax):
    frameg = pd.DataFrame(
        columns=["Open", "High", "Low", "Close", "Volume"], index=frame.index
    )
    framer = pd.DataFrame(
        columns=["Open", "High", "Low", "Close", "Volume"], index=frame.index
    )
    for i in range(len(frame)):
        if frame["Close"].iloc[i] >= frame["Open"].iloc[i]:
            frameg.loc[frame.index[i]] = [
                frame["Open"].iloc[i],
                frame["High"].iloc[i],
                frame["Low"].iloc[i],
                frame["Close"].iloc[i],
                frame["Volume"].iloc[i],
            ]
        else:
            framer.loc[frame.index[i]] = [
                frame["Open"].iloc[i],
                frame["High"].iloc[i],
                frame["Low"].iloc[i],
                frame["Close"].iloc[i],
                frame["Volume"].iloc[i],
            ]

    barw = 0.003
    linew = 0.5
    ax.bar(frameg.index, frameg["Close"], width=barw, color=color["green"])
    ax.bar(frameg.index, frameg["Open"], width=barw, color=color["black"])
    for i in range(len(frameg)):
        if frameg["Open"] is not np.nan:
            time = []
            price = []
            time.append(frameg.index[i])
            time.append(frameg.index[i])
            price.append(frameg["Low"].iloc[i])
            price.append(frameg["High"].iloc[i])
            ax.plot(time, price, color=color["green"], linewidth=linew)

    ax.bar(framer.index, framer["Open"], width=barw, color=color["red"])
    ax.bar(framer.index, framer["Close"], width=barw, color=color["black"])
    for i in range(len(framer)):
        if framer["Open"] is not np.nan:
            time = []
            price = []
            time.append(framer.index[i])
            time.append(framer.index[i])
            price.append(framer["Low"].iloc[i])
            price.append(framer["High"].iloc[i])
            ax.plot(time, price, color=color["red"], linewidth=linew)

    ax.set_ylim([min(frame["Low"]) * 0.998, max(frame["High"]) * 1.002])
    ax.set_ylabel("Price", color=color["lgrey"])
    ax.spines["bottom"].set_color(color["lgrey"])
    ax.spines["top"].set_color(color["lgrey"])
    ax.spines["right"].set_color(color["lgrey"])
    ax.spines["left"].set_color(color["lgrey"])
    ax.tick_params(axis="x", colors=color["lgrey"])
    ax.tick_params(axis="y", colors=color["lgrey"])
    ax.set_facecolor(color["black"])


#  plot the trade
#  greenish white line indicating a profitable trade
#  reddish white line indicating a loss trade
def plottrade(frame, ax, trade, criteria=[]):
    if criteria == []:
        for i in range(len(trade)):
            x = [trade[i][1], trade[i][3]]
            y = [trade[i][2], trade[i][4]]
            if trade[i][2] <= trade[i][4] * 0.998:
                ax.plot(x, y, color=color["gwhite"], linewidth=2)
            else:
                ax.plot(x, y, color=color["rwhite"], linewidth=2)
    else:
        for i in range(len(trade)):
            if trade[i][0] in criteria:
                x = [trade[i][1], trade[i][3]]
                y = [trade[i][2], trade[i][4]]
                if trade[i][2] <= trade[i][4] * 0.998:
                    ax.plot(x, y, color=color["gwhite"], linewidth=2)
                else:
                    ax.plot(x, y, color=color["rwhite"], linewidth=2)


#  plots the candlestick, trade and also the indicators below the candlestick chart
#  ind is the data used for the indicators
#  ind = [[ind1.1, ind1.2, .., ind1.n], .., [indn.1, .., indn.n]]
#  indl is the label for the indicators
#  indl = [[lind1.1, lind1.2, .., lind1.n], .., [lindn.1, .., lindn.n]]
#  trade is the list of transaction done
def plotall(frame, ind, indl, trade=[], criteria=[], islabel=True):
    if len(ind) <= 1:
        fig, ax = plt.subplots(nrows=1, ncols=1, facecolor=color["black"])
        candlestick(frame, ax)
        for j in range(len(ind[0])):
            x = frame.index
            y = ind[0][j]
            if islabel:
                ax.plot(x, y, color=color[j], label=indl[0][j], linewidth=0.7)
            else:
                ax.plot(x, y, color=color[j], linewidth=0.7)
        plottrade(frame, ax, trade, criteria)
        if islabel:
            ax.legend()
    else:
        heightratio = [3, 1]
        if len(ind) > 2:
            for p in range(2, len(ind)):
                heightratio.append(1)
        fig, axs = plt.subplots(
            nrows=len(ind),
            ncols=1,
            facecolor=color["black"],
            gridspec_kw={"height_ratios": heightratio},
        )
        candlestick(frame, axs[0])
        for i in range(len(ind)):
            for j in range(len(ind[i])):
                x = frame.index
                y = ind[i][j]
                if islabel:
                    axs[i].plot(x, y, color[j], label=indl[i][j], linewidth=0.7)
                else:
                    axs[i].plot(x, y, color[j], linewidth=0.7)
                axs[i].spines["bottom"].set_color(color["lgrey"])
                axs[i].spines["top"].set_color(color["lgrey"])
                axs[i].spines["right"].set_color(color["lgrey"])
                axs[i].spines["left"].set_color(color["lgrey"])
                axs[i].tick_params(axis="x", colors=color["lgrey"])
                axs[i].tick_params(axis="y", colors=color["lgrey"])
                axs[i].set_facecolor(color["black"])
                if indl[i][j] == "RSI":
                    axs[i].set_ylim([0, 100])
                    x = [frame.index[0], frame.index[-1]]
                    l = [30, 30]
                    m = [50, 50]
                    h = [70, 70]
                    axs[i].plot(x, l, color=color[2], linewidth=0.7)
                    axs[i].plot(x, m, color=color[1], linestyle="--", linewidth=0.7)
                    axs[i].plot(x, h, color=color[2], linewidth=0.7)
                elif indl[i][j] == "Stoch.K":
                    axs[i].set_ylim([0, 100])
                    x = [frame.index[0], frame.index[-1]]
                    l = [20, 20]
                    h = [80, 80]
                    axs[i].plot(x, l, color=color[2], linewidth=0.7)
                    axs[i].plot(x, h, color=color[2], linewidth=0.7)
                elif indl[i][j] == "MACD":
                    x = [frame.index[0], frame.index[-1]]
                    b = [0, 0]
                    axs[i].plot(x, b, color=color[2], linewidth=0.7)

                if "Reg" in indl[i][j]:
                    x = [frame.index[0], frame.index[-1]]
                    b = [0, 0]
                    axs[i].plot(x, b, color=color[2], linewidth=0.7)

            if islabel:
                axs[i].legend()
        plottrade(frame, axs[0], trade, criteria)
    fig.subplots_adjust(hspace=0)
    if len(ind) == 1:
        ax.set_xlabel("Time", color=color["lgrey"])
    else:
        axs[len(ind) - 1].set_xlabel("Time", color=color["lgrey"])


# STANDARD BACKTESTING
# CRYPTO = ''
# mainint = ''
# intervals = [mainint]
# lblen = num (greater number)
# cut = num (smaller number)
# strat = stratname
# lookback = lbgen(mainint, lblen)
# tradehis = tester(CRYPTO, intervals, lblen, strat, cut)
# for i in tradehis:
#     print(i)
# tradesum(tradehis, crit=True)
#
# test = getcleanind(CRYPTO, mainint, lookback, indicators[strat])
# if cut != 0:
#     test = test.iloc[:-cut]
# ind = [[test['EMA50'], test['EMA100'], test['EMA200']], [test['RSI']], [test['Stoch.K'], test['Stoch.D']], [test['MACD'], test['MACD.Sign']]]
# indl = [['EMA50', 'EMA100', 'EMA200'], ['RSI'], ['Stoch.K', 'Stoch.D'], ['MACD', 'MACD.Sign']]
# plotall(test, ind, indl, tradehis, criteria=[])
# plt.show()


CRYPTO = "ETHUSDT"
mainint = "1h"
intervals = [mainint]
lblen = 200
cut = 0
strat = strat2test
lookback = lbgen(mainint, lblen)
tradehis = tester(CRYPTO, intervals, lblen, strat, cut)
for i in tradehis:
    print(i)
tradesum(tradehis, crit=True, lvg=1)

test = getcleanind(CRYPTO, mainint, lookback, indicators[strat])
if cut != 0:
    test = test.iloc[:-cut]
indl = [
    ["EMA50", "EMA100", "EMA200"],
    ["RSI", "RSI.SMA30", "RSI.SMA50"],
    ["Stoch.K", "Stoch.D"],
    ["MACD", "MACD.Sign"],
    ["REG", "REG.SMA3"],
]
ind = []
for i in range(len(indl)):
    ind.append([])
    for j in range(len(indl[i])):
        ind[i].append(test[indl[i][j]])


plotall(test, ind, indl, tradehis, islabel=True)
plt.show()
