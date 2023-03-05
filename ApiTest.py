# Using this to test API implementation and eventually paper testing #
import time
import requests
import urllib.parse
import hashlib
import hmac
import base64

with open('keys', 'r') as k:
    keys = k.read().splitlines()
    api_key = keys[0]
    api_sec = keys[1]

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
