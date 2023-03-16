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

with open('keys', 'r') as k:
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



ohlc = k.get_ohlc_data('ETHUSD', interval=1440, ascending = True)

ohlc[0][f'SMA_{200}'] = ohlc[0]['close'].rolling(window=200).mean()
ohlc[0][f'SMA_{5}'] = ohlc[0]['close'].rolling(window=5).mean()

#print(ohlc[0].tail())



#plt.style.use('dark_background')
#fig, axs = plt.subplots(2)
#axs[0].plot(ohlc[0]['close'], label='Share Price', alpha=0.5)
#axs[0].plot(ohlc[0][f'SMA_{200}'], label=f'SMA_{200}', color='orange')
#axs[0].plot(ohlc[0][f'SMA_{5}'], label=f'SMA_{5}', color='purple', linestyle='--')
#fig.legend(loc='upper left')
#plt.show()