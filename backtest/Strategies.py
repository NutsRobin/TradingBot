# Contains functions for each strategy that can be called for
# back testing or paper testing
import pandas as pd
import matplotlib.pyplot as plt

strats = set(('rsi-2', 'standard-mva'))

def rsi_strat(df, period, buy_signals, sell_signals, balance, eth_bal):
    diff = 0
    gain = 0
    avg_gain = 0
    avg_loss = 0
    loss = 0
    trigger = -1
    trigger_short = -2
    rsi_vals = []
    trades = []
    ma_5 = 5
    ma_200 = 200
    day = 0

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
            
            # Long logic #
            if df['Adj Close'].iloc[x] > df[f'SMA_{ma_200}'].iloc[x]:
                if trigger_short == 2:
                    #print("Close Short\n")
                    trigger_short = -2

                if rsi_vals[-1] <= 20 and trigger != 1 and df['Adj Close'].iloc[x] > df[f'SMA_{ma_200}'].iloc[x]:
                    buy_signals.append(df['Adj Close'].iloc[x])
                    sell_signals.append(float('nan'))
                    trigger = 1
                    prev_buy = balance
                    eth_bal = balance/(df['Adj Close'].iloc[x])
                    balance = 0
                    day = x
                elif rsi_vals[-1] > 80 and trigger != -1 and df['Adj Close'].iloc[x] > df[f'SMA_{ma_5}'].iloc[x]:
                    sell_signals.append(df['Adj Close'].iloc[x])
                    buy_signals.append(float('nan'))
                    trigger = -1
                    balance = eth_bal*(df['Adj Close'].iloc[x])
                    eth_bal = 0
                    day_diff = x - day
                    trades.append([prev_buy, balance, balance-prev_buy, day_diff])
                else:
                    buy_signals.append(float('nan'))
                    sell_signals.append(float('nan'))

            # Short logic #
            # does not actually test short selling, but is the start of the logic #
            # will get to testing short selling once the long trading stategy is complete #
            elif df['Adj Close'].iloc[x] < df[f'SMA_{ma_200}'].iloc[x] and balance > 0:
                buy_signals.append(float('nan'))
                sell_signals.append(float('nan'))
                if df['Adj Close'].iloc[x] < df[f'SMA_{ma_200}'].iloc[x] and trigger_short != 2 and rsi_vals[-1] > 90:
                    #print("Open Short")
                    trigger_short = 2
                elif rsi_vals[-1] < 10 and trigger_short != -2 and df['Adj Close'].iloc[x] < df[f'SMA_{ma_5}'].iloc[x]:
                    #print("Close Short\n")
                    trigger_short = -2

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
    print(f'Total Growth: {round(growth*100,2)}% or ${balance-1000.00}')
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

def std_mva(df, buy_signals, sell_signals, balance, eth_bal):
    ma_1 = 10
    ma_2 = 30
    trigger = -1
    trades = []
    day = 0

    df[f'SMA_{ma_1}'] = df['Adj Close'].rolling(window=ma_1).mean()
    df[f'SMA_{ma_2}'] = df['Adj Close'].rolling(window=ma_2).mean()
    df = df.iloc[ma_2:]

    for x in range(len(df)):
        if df[f'SMA_{ma_1}'].iloc[x] > df[f'SMA_{ma_2}'].iloc[x] and trigger != 1:
            buy_signals.append(df['Adj Close'].iloc[x])
            sell_signals.append(float('nan'))
            prev_buy = balance
            trigger = 1
            eth_bal = balance/(df['Adj Close'].iloc[x])
            balance = 0
            day = x
        elif df[f'SMA_{ma_1}'].iloc[x] < df[f'SMA_{ma_2}'].iloc[x] and trigger != -1:
            buy_signals.append(float('nan'))
            sell_signals.append(df['Adj Close'].iloc[x])
            trigger = -1
            balance = eth_bal*(df['Adj Close'].iloc[x])
            eth_bal = 0
            day_diff = x -day
            trades.append([prev_buy, balance, balance-prev_buy, day_diff])
        else:
            buy_signals.append(float('nan'))
            sell_signals.append(float('nan'))

    df['Buy Signals'] = buy_signals
    df['Sell Signals'] = sell_signals

    if (balance == 0):
        balance = eth_bal*(df['Adj Close'].iloc[-1])

    # some calculations, will expand the info given here
    growth = (balance-1000.00)/1000
    print(f'Current Account Value: {balance}')
    print(f'Total Growth: {round(growth*100,2)}% or ${balance-1000.00}')
    analyze_trades(trades)

    plt.plot(df[f'SMA_{ma_1}'], label=f'SMA_{ma_1}', color='orange', linestyle='--')
    plt.plot(df[f'SMA_{ma_2}'], label=f'SMA_{ma_2}', color='pink', linestyle='--')
    plt.plot(df['Adj Close'], label='Share Price', alpha=0.5)
    plt.scatter(df.index, df['Buy Signals'], label='Buy Signal', marker='^', color='#00ff00', lw=3)
    plt.scatter(df.index, df['Sell Signals'], label='Sell Signal', marker='v', color='#ff0000', lw=3)
    plt.legend(loc='upper left')
    plt.show()

# Supporting functions for main strategies #
def calc_rsi(rs):
    rsi = 100 - (100/(1+rs))
    return rsi
    
def analyze_trades(trades):
    trade_df = pd.DataFrame(trades, columns=['buy_price', 'sell_price', 'difference', 'duration'])
    

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