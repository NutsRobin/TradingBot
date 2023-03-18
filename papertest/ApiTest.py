# Using this to test API implementation and eventually paper testing #
import time
import requests
import urllib.parse
import hashlib
import hmac
import base64
import pykrakenapi as pyk
import krakenex
import matplotlib.pyplot as plt

with open('papertest/keys', 'r') as k:
    keys = k.read().splitlines()
    api_key = keys[0]
    api_sec = keys[1]

api = krakenex.API()
k = pyk.KrakenAPI(api)

api_url = 'https://api.kraken.com'

def kraken_signature(url_path, data, sec):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = url_path.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(sec), message, hashlib.sha512)
    sig_digest = base64.b64encode(mac.digest())
    return sig_digest.decode()


def gen_request(url_path, data, api_key, sec):
    signature = kraken_signature(url_path, data, sec)
    headers = {'API-KEY' : api_key, 'API-SIGN' : signature}
    resp = requests.post((api_url+url_path), headers=headers, data=data)
    return resp

def get_account_bal():
    return gen_request("/0/private/Balance", {"nonce": str(int(1000*time.time()))}, api_key, api_sec)

def get_curr_price():
    currPrice = requests.get("https://api.kraken.com/0/public/Ticker?pair=ETHUSD").json()['result']['XETHZUSD']
    return currPrice

def calc_rsi(rs):
    rsi = 100 - (100/(1+rs))
    return rsi

def rsi_2(ohlc):
    period = 2
    gain = 0
    loss = 0
    rsi_vals = []
    for x in range(1, len(ohlc[0])):
        curr_price = ohlc[0]['close'].iloc[x]
        past_price = ohlc[0]['close'].iloc[x-1]
        diff = curr_price - past_price

        if (x < period+1):
            if (diff < 0):
                loss += abs(diff)
                rsi_vals.append(0)
            else:
                gain += diff
                rsi_vals.append(0)
            
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

    return rsi_vals


# get public historical data
try:
    ohlc = k.get_ohlc_data('ETHUSD', interval=1440, ascending = True,)
except Exception as e:
    print(f'Failed to retrieve OHLC data: {e}')

# get rsi vals
ohlc[0]['rsi-2'] = rsi_2(ohlc)

# Get moving averages
ohlc[0][f'SMA_{200}'] = ohlc[0]['close'].rolling(window=200).mean()
ohlc[0][f'SMA_{5}'] = ohlc[0]['close'].rolling(window=5).mean()

trigger = -1
sma200 = ohlc[0][f'SMA_{200}'].iloc[-1]
rsi2 = ohlc[0]['rsi-2'].iloc[-1]
while (1):
    # get current ETH price
    try:
        ethPrice = float((k.get_ticker_information('ETHUSD'))['b'][0][0])
        print(f'ETH price: {ethPrice} - SMA200: {sma200} - RSI-2: {rsi2}')
    except Exception as e:
        print(f'Failed to retrieve ETH data: {e}')

    # long trade logic
    if ethPrice > ohlc[0][f'SMA_{200}'].iloc[-1]:
        if ohlc[0]['rsi-2'].iloc[-1] <= 20 and trigger != 1:
            print("Buy ETH here")
        elif ohlc[0]['rsi-2'].iloc[-1] > 80 and trigger != -1 and ethPrice > ohlc[0][f'SMA_{5}'].iloc[-1]:
            print("Sell ETH here")
        else:
            print("Do nothing")
    
    time.sleep(10)


print(ohlc[0].head())

plt.style.use('dark_background')
fig, axs = plt.subplots(2)
axs[0].plot(ohlc[0]['close'], label='Share Price', alpha=0.5)
axs[0].plot(ohlc[0][f'SMA_{200}'], label=f'SMA_{200}', color='orange')
axs[0].plot(ohlc[0][f'SMA_{5}'], label=f'SMA_{5}', color='purple', linestyle='--')
axs[1].plot(ohlc[0]['rsi-2'], label='RSI', color='pink', linestyle='--')
axs[1].axhline(y=80, label='RSI HIGH', color='blue', linestyle='--')
axs[1].axhline(y=20, label='RSI LOW', color='orange', linestyle='--')
fig.legend(loc='upper left')
plt.show()