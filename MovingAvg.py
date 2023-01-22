import datetime as dt
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import yfinance as yf

plt.style.use("dark_background")

ma_1 = 21
ma_2 = 144
balance = 1000.00
eth_bal = 0.00


start_date = dt.datetime.now() - dt.timedelta(days=365)
end_date = dt.datetime.now()

yf.pdr_override()
df = pdr.data.get_data_yahoo("ETH-USD", start=start_date, end=end_date)
df[f'SMA_{ma_1}'] = df['Adj Close'].rolling(window=ma_1).mean()
df[f'SMA_{ma_2}'] = df['Adj Close'].rolling(window=ma_2).mean()

df = df.iloc[ma_2:]

#plt.plot(df['Adj Close'], label='Share Price', color='lightgray')
#plt.plot(df[f'SMA_{ma_1}'], label=f'SMA_{ma_1}', color='orange')
#plt.plot(df[f'SMA_{ma_2}'], label=f'SMA_{ma_2}', color='purple')
#plt.legend(loc='upper left')
#plt.show()

buy_signals = []
sell_signals = []
trigger = 0

for x in range(len(df)):
    if df[f'SMA_{ma_1}'].iloc[x] > df[f'SMA_{ma_2}'].iloc[x] and trigger != 1:
        buy_signals.append(df['Adj Close'].iloc[x])
        sell_signals.append(float('nan'))
        trigger = 1
        
    elif df[f'SMA_{ma_1}'].iloc[x] < df[f'SMA_{ma_2}'].iloc[x] and trigger != -1:
        buy_signals.append(float('nan'))
        sell_signals.append(df['Adj Close'].iloc[x])
        trigger = -1
    else:
        buy_signals.append(float('nan'))
        sell_signals.append(float('nan'))

df['Buy Signals'] = buy_signals
df['Sell Signals'] = sell_signals
print(df)

plt.plot(df['Adj Close'], label='Share Price', alpha=0.5)
plt.plot(df[f'SMA_{ma_1}'], label=f'SMA_{ma_1}', color='orange', linestyle='--')
plt.plot(df[f'SMA_{ma_2}'], label=f'SMA_{ma_2}', color='pink', linestyle='--')
plt.scatter(df.index, df['Buy Signals'], label='Buy Signal', marker='^', color='#00ff00', lw=3)
plt.scatter(df.index, df['Sell Signals'], label='Sell Signal', marker='v', color='#ff0000', lw=3)
plt.legend(loc='upper left')
plt.show()