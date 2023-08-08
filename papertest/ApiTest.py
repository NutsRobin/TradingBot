# Using this to test API implementation and eventually paper testing #
import time
from datetime import datetime
import requests
import urllib.parse
import hashlib
import hmac
import base64
import pykrakenapi as pyk
import krakenex

"""
kraken_signature is used for verification with the kraken api
https://docs.kraken.com/rest/#section/Authentication/Headers-and-Signature
"""
def kraken_signature(url_path, data, sec):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = url_path.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(sec), message, hashlib.sha512)
    sig_digest = base64.b64encode(mac.digest())
    return sig_digest.decode()


"""
gen_request is the base function for the more specific api request functions

url_path: path for request
data: required data for the request
api_key: kraken api key
sec: the api_sec that is generated with the api key
return: a kraken response
"""
def gen_request(url_path, data, api_key, sec):
    signature = kraken_signature(url_path, data, sec)
    headers = {'API-KEY' : api_key, 'API-SIGN' : signature}
    resp = requests.post((api_url+url_path), headers=headers, data=data)
    return resp

"""
get_account_bal is used to gather balances on the kraken account

return: kraken resp containing account balances or an error
"""
def get_account_bal():
    return gen_request("/0/private/Balance", {"nonce": str(int(1000*time.time()))}, api_key, api_sec)


"""
get_curr_price requests the current price of Ethereum in USD

return: value of ETH in USD or error
"""
def get_curr_price():
    currPrice = requests.get("https://api.kraken.com/0/public/Ticker?pair=ETHUSD").json()['result']['XETHZUSD']
    return currPrice


"""
calc_rsi is used to calculate a rsi value with the given rs value

rs: ((average gain * period-1) + curr_gain)/((average loss * period-1) + current loss)
return: a Relative Strength Index value
"""
def calc_rsi(rs):
    rsi = 100 - (100/(1+rs))
    return rsi


"""
rsi_2 calculates a 2 day period Relative Strength Index based on each given day's closing value

ohlc: kraken historical data as a pandas dataframe
return: list of RSI values ordered by date
"""
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
                if avg_loss == 0:
                    rsi_vals.append(100)
                else: 
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
            if avg_loss == 0:
                rs = 100
            else:
                rs = avg_gain/avg_loss
            rsi_vals.append(calc_rsi(rs))

    return rsi_vals

"""
hist_data retireves the ohlc data using the kraken api

return: dataframe of historical data
"""
def hist_data():
    # get public historical data
    print("Getting ohlc data")
    try:
        ohlc = k.get_ohlc_data('ETHUSD', interval=1440, ascending = True,)
    except Exception as e:
        print(f'Failed to retrieve OHLC data: {e}')
    
    return ohlc

with open('papertest/keys', 'r') as k:
    keys = k.read().splitlines()
    api_key = keys[0]
    api_sec = keys[1]

api = krakenex.API()
k = pyk.KrakenAPI(api)

api_url = 'https://api.kraken.com'

trigger = -1
usdBalance = 1000
ethBalance = 0
while (1):
    ohlc = hist_data()

    # get rsi vals
    ohlc[0]['rsi-2'] = rsi_2(ohlc)

    # Get moving averages
    ohlc[0][f'SMA_{200}'] = ohlc[0]['close'].rolling(window=200).mean()
    ohlc[0][f'SMA_{5}'] = ohlc[0]['close'].rolling(window=5).mean()

    sma200 = ohlc[0][f'SMA_{200}'].iloc[-1]
    sma5 = ohlc[0][f'SMA_{5}'].iloc[-1]
    rsi2 = ohlc[0]['rsi-2'].iloc[-1]
    time.sleep(5)

    if ((rsi2 <= 20 and trigger == -1) or (rsi2 > 80 and trigger == 1)):
        print("trading time")
        total = 0
        for i in range(8502):
            # this takes 0.13 seconds
            # get current ETH price
            try:
                ethPrice = float((k.get_ticker_information('ETHUSD'))['b'][0][0])
                #print(f'ETH price: {ethPrice} - SMA200: {sma200} - SMA5: {sma5} - RSI-2: {rsi2}')
            except Exception as e:
                print(f'Failed to retrieve ETH data: {e}')    

            if ethPrice > sma200:
                if (trigger == -1):
                    print(f'***Buying ETH for {ethPrice}***')

                    ethBalance = usdBalance/ethPrice
                    usdBalance = 0
                    with open('trades.txt', 'w') as trades:
                        trades.write(f'{datetime.now()},{ethPrice},nan,{ethBalance},{usdBalance}')
                    trigger = 1
                    time.sleep(10.16*(8502-i))
                elif (trigger == 1 and ethPrice > sma5):
                    print(f'***Selling ETH for {ethPrice}***')

                    usdBalance = ethBalance*ethPrice
                    ethBalance = 0
                    with open('trades.txt', 'w') as trades:
                        trades.write(f'{datetime.now()},nan,{ethPrice},{ethBalance},{usdBalance}')
                    trigger = -1
                    time.sleep(10.16*(8502-i))
            time.sleep(10)
            
    else:
        # sleep for 24 hours (minus 5 seconds for ohlc time) - 86395
        print("no trades today, see ya tomorrow!")
        time.sleep(86395)