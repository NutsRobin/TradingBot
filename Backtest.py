import datetime as dt
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import pandas as pd
import yfinance as yf

plt.style.use("dark_background")

buy_signals = []
sell_signals = []
balance = 1000.00
eth_bal = 0.0

start_date = dt.datetime.now() - dt.timedelta(days=365*3)
end_date = dt.datetime.now()

# gather data from yahoo finance from given dates #
yf.pdr_override()
df = pdr.data.get_data_yahoo("ETH-USD", start=start_date, end=end_date)

# calculate RSI given rs #
def calc_rsi(rs):
    rsi = 100 - (100/(1+rs))
    return rsi

def analyze_trades(trades):
    trade_df = pd.DataFrame(trades, columns=['buy_price', 'sell_price', 'difference'])
    

    num_trades = len(trade_df)
    avg_trade_val = trade_df['difference'].mean()

    gains = trade_df[(trade_df['difference'] > 0)]
    perc_gain = float(len(gains)/len(trade_df))
    avg_gain = gains['difference'].mean()
    max_gain = gains['difference'].max()
    min_gain = gains['difference'].min()

    losses = trade_df[(trade_df['difference'] < 0)]
    perc_loss = float(len(losses)/len(trade_df))
    avg_loss = losses['difference'].mean()
    max_loss = losses['difference'].min()
    min_loss = losses['difference'].max()

    print(f'{trade_df}\nNumber of Trades: {num_trades}\nAverage Trade Value: {avg_trade_val}\n')
    print(f'Gain%: {perc_gain}\nAverage Gain: {avg_gain}\nMax Gain: {max_gain}\nMin Gain: {min_gain}\n')
    print(f'Loss%: {perc_loss}\nAverage Loss: {avg_loss}\nMax Loss: {max_loss}\nMin Loss: {min_loss}') 

# Uses RSI interval to determine when to buy/sell #
def rsi_strat(df, period, buy_signals, sell_signals, balance, eth_bal):
    diff = 0
    gain = 0
    avg_gain = 0
    avg_loss = 0
    loss = 0
    trigger = -1
    rsi_vals = []
    trades = []
    ma_5 = 5
    ma_200 = 200

    ## Moving average calculations
    df[f'SMA_{ma_5}'] = df['Adj Close'].rolling(window=ma_5).mean()
    df[f'SMA_{ma_200}'] = df['Adj Close'].rolling(window=ma_200).mean()
    df = df.iloc[ma_200:]

    for x in range(1, len(df)):
        curr_price = df['Adj Close'].iloc[x]
        past_price = df['Adj Close'].iloc[x-1]
        diff = curr_price - past_price

        if (x < period+1):
            if (diff < 0):
                loss += abs(diff)
            else:
                gain += diff
            
            # first avg
            if (x == period):
                avg_gain = gain/x
                avg_loss = loss/x
                rs = avg_gain/avg_loss
                rsi_vals.append(calc_rsi(rs))
        
        else:
            if (diff < 0):
                loss = abs(diff)
                gain = 0
            else:
                gain = diff
                loss = 0

            avg_gain = ((avg_gain*(period-1)) + gain)/period
            avg_loss = ((avg_loss*(period-1)) + loss)/period
            rs = avg_gain/avg_loss
            rsi_vals.append(calc_rsi(rs))

            if rsi_vals[-1] <= 20 and trigger != 1 and df['Adj Close'].iloc[x] > df[f'SMA_{ma_200}'].iloc[x]:
                buy_signals.append(df['Adj Close'].iloc[x])
                sell_signals.append(float('nan'))
                trigger = 1
                prev_buy = balance
                eth_bal = balance/(df['Adj Close'].iloc[x])
                balance = 0

            elif rsi_vals[-1] > 80 and trigger != -1 and df['Adj Close'].iloc[x] > df[f'SMA_{ma_5}'].iloc[x]:
                sell_signals.append(df['Adj Close'].iloc[x])
                buy_signals.append(float('nan'))
                trigger = -1
                balance = eth_bal*(df['Adj Close'].iloc[x])
                eth_bal = 0
                trades.append([prev_buy, balance, balance-prev_buy])

            else:
                buy_signals.append(float('nan'))
                sell_signals.append(float('nan'))
    
    df = df.iloc[period+1:]
    df['Buy Signals'] = buy_signals
    df['Sell Signals'] = sell_signals

    if (balance == 0):
        balance = eth_bal*(df['Adj Close'].iloc[-1])

    # some calculations, will expand the info given here
    growth = (balance-1000.00)/1000
    print(f'Current Account Value: {balance}')
    print(f'Total Growth: {growth} or {balance-1000.00}')
    analyze_trades(trades)

    # plots the RSI and daily adjusted close share prices
    fig, axs = plt.subplots(2)
    axs[0].plot(df['Adj Close'], label='Share Price', alpha=0.5)
    axs[0].plot(df[f'SMA_{ma_200}'], label=f'SMA_{ma_200}', color='orange')
    axs[0].plot(df[f'SMA_{ma_5}'], label=f'SMA_{ma_5}', color='purple', linestyle='--')
    axs[0].scatter(df.index, df['Buy Signals'], label='Buy Signal', marker='^', color='#00ff00', lw=3)
    axs[0].scatter(df.index, df['Sell Signals'], label='Sell Signal', marker='v', color='#ff0000', lw=3)
    axs[1].plot(rsi_vals, label='RSI', color='pink', linestyle='--')
    axs[1].axhline(y=80, label='RSI HIGH', color='blue', linestyle='--')
    axs[1].axhline(y=20, label='RSI LOW', color='orange', linestyle='--')
    fig.legend(loc='upper left')
    plt.show()

rsi_strat(df, 2, buy_signals, sell_signals, balance, eth_bal)

            
# basic moving average cross over strat used for testing #
def calc_mva(df, buy_signals, sell_signals, balance, eth_bal):
    ma_1 = 10
    ma_2 = 30
    trigger = -1

    df = df.iloc[ma_2:]

    for x in range(len(df)):
        if df[f'SMA_{ma_1}'].iloc[x] > df[f'SMA_{ma_2}'].iloc[x] and trigger != 1:
            buy_signals.append(df['Adj Close'].iloc[x])
            sell_signals.append(float('nan'))
            trigger = 1
            eth_bal = balance/(df['Adj Close'].iloc[x])
            balance = 0
            print(f'ETH: {eth_bal}')
            print(f'USD: {balance}\n')
        elif df[f'SMA_{ma_1}'].iloc[x] < df[f'SMA_{ma_2}'].iloc[x] and trigger != -1:
            buy_signals.append(float('nan'))
            sell_signals.append(df['Adj Close'].iloc[x])
            trigger = -1
            balance = eth_bal*(df['Adj Close'].iloc[x])
            eth_bal = 0
            print(f'ETH: {eth_bal}')
            print(f'USD: {balance}\n')
        else:
            buy_signals.append(float('nan'))
            sell_signals.append(float('nan'))

    df['Buy Signals'] = buy_signals
    df['Sell Signals'] = sell_signals

    if (balance == 0):
        balance = eth_bal*(df['Adj Close'].iloc[-1])

    growth = (balance-1000.00)/1000
    print(f'Final Balance: {balance}')
    print(f'Total Growth: {growth} or {balance-1000.00}')

    plt.plot(df[f'SMA_{ma_1}'], label=f'SMA_{ma_1}', color='orange', linestyle='--')
    plt.plot(df[f'SMA_{ma_2}'], label=f'SMA_{ma_2}', color='pink', linestyle='--')
    plt.plot(df['Adj Close'], label='Share Price', alpha=0.5)
    plt.scatter(df.index, df['Buy Signals'], label='Buy Signal', marker='^', color='#00ff00', lw=3)
    plt.scatter(df.index, df['Sell Signals'], label='Sell Signal', marker='v', color='#ff0000', lw=3)
    plt.legend(loc='upper left')
    plt.show()

#calc_mva(df, buy_signals, sell_signals, balance, eth_bal)