import datetime as dt
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import pandas as pd
import yfinance as yf
import sys
import Strategies as strat

"""
handle_args is to ensure proper usage of Backtest.py arguments

return: return the argument if it is valid
"""
def handle_args():
    if (len(sys.argv) != 2):
        sys.exit('Invalid usage\nUsage: python3 Backtest.py [strategy]')
    if (sys.argv[1] not in strat.strats):
        sys.exit(f'Invalid argument.\nValid strategies: {strat.strats}')
    return sys.argv[1]

    

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

strategy = handle_args()
if (strategy == 'rsi-2'):
    strat.rsi_strat(df, 2, buy_signals, sell_signals, balance, eth_bal)
elif (strategy == 'standard-mva'):
    strat.std_mva(df, buy_signals, sell_signals, balance, eth_bal)