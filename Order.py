#!/usr/bin/env python3

import requests
import time
import hashlib
import hmac
import base64
import json
import sqlite3

from collections import OrderedDict
from config import apikey_secret
from config import apikey_public
from config import domain
from config import database_file

# Define Global Vars
#uri = "/account/balance"
#url = domain + uri
askey = apikey_secret.encode("utf-8")
pkey = apikey_public.encode("utf-8")
skey = base64.standard_b64decode(askey)

def build_headers(URI, PUBKEY, PRIVKEY, PAYLOAD):
    """Build timestamp, format and encode everything,  and construct string to 
    sign with api key. Use HmacSHA512 algorithm in order to sign.
    
    Lastly build the headers to send... In order to ensure the correct order 
    of key value pairs in the JSON payload, build an ordered dictionary out
    of a list of tuples.
    """
    # Build timestamp
    #tstamp = time.time()
    #ctstamp = int(tstamp * 1000)  # or int(tstamp * 1000) or round(tstamp * 1000)
    #sctstamp = str(ctstamp)
    sctstamp = str(int(time.time() * 1000))
       
    # Build and sign to construct body
    #sbody = uri + "\n" + sctstamp + "\n"
    sbody = URI  + "\n" + sctstamp + "\n" + str(PAYLOAD)
    print(sbody)
    rbody = sbody.encode("utf-8")
    rsig = hmac.new(skey, rbody, hashlib.sha512)
    bsig = base64.standard_b64encode(rsig.digest()).decode("utf-8")
    
    # Construct header list of key value pairs
    headers_list = OrderedDict([("Accept", "application/json"),
                     ("Accept-Charset", "UTF-8"),
                     ("Content-Type", "application/json"),
                     ("apikey", pkey),
                     ("timestamp", sctstamp),
                     ("signature", bsig)])
    # Load list into dictionary
    headers = dict(headers_list)
    
    return headers

def OrderHistory():
    uri="/order/history"

    payload = {"currency":"AUD","instrument":"BTC","limit":20,"since":33434568724}
    res = build_headers(uri, pkey, skey, payload)
    print(res)
    
    r = requests.post(domain+uri, headers=res, data=json.dumps(payload), verify=True)
    print(r.text)

def main():
    OrderHistory()

if __name__ == "__main__":
    main()