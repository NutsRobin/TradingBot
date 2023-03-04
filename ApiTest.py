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

#def kraken_signature():