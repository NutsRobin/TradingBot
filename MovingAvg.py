import datetime as dt
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import yfinance as yf

plt.style.use("dark_background")

ma_1 = 8
ma_2 = 39
balance = 1000.00
eth_bal = 0.0


start_date = dt.datetime.now() - dt.timedelta(days=180)
end_date = dt.datetime.now()

yf.pdr_override()
df = pdr.data.get_data_yahoo("ETH-USD", start=start_date, end=end_date)
df[f'SMA_{ma_1}'] = df['Adj Close'].rolling(window=ma_1).mean()
df[f'SMA_{ma_2}'] = df['Adj Close'].rolling(window=ma_2).mean()

df = df.iloc[ma_2:]

buy_signals = []
sell_signals = []
trigger = -1

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

plt.plot(df['Adj Close'], label='Share Price', alpha=0.5)
plt.plot(df[f'SMA_{ma_1}'], label=f'SMA_{ma_1}', color='orange', linestyle='--')
plt.plot(df[f'SMA_{ma_2}'], label=f'SMA_{ma_2}', color='pink', linestyle='--')
plt.scatter(df.index, df['Buy Signals'], label='Buy Signal', marker='^', color='#00ff00', lw=3)
plt.scatter(df.index, df['Sell Signals'], label='Sell Signal', marker='v', color='#ff0000', lw=3)
plt.legend(loc='upper left')
plt.show()