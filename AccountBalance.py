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
uri = "/account/balance"
#url = domain + uri
askey = apikey_secret.encode("utf-8")
pkey = apikey_public.encode("utf-8")
skey = base64.standard_b64decode(askey)

def build_headers(URI, PUBKEY, PRIVKEY):
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
    sbody = URI  + "\n" + sctstamp + "\n"
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

dataDict = {}

def WriteToDb():
    try:
        conn = sqlite3.connect(database_file)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='AccountStatus';")
        if len(cur.fetchall()) == 0:
            cur.execute(''' create table AccountStatus
            (AUD text, BCH text, BTC text, ETC text, ETH text, LTC text, TIME text, XRP text)''')

        # Table exists or created, now add values
        #print(dataDict["AUD"], dataDict["BCH"], dataDict["BTC"], dataDict["ETC"], dataDict["ETH"], dataDict["LTC"], dataDict["TIME"], dataDict["XRP"])
        cur.execute("insert into AccountStatus(AUD, BCH, BTC, ETC, ETH, LTC, TIME, XRP ) values (?, ?, ?, ?, ?, ?, ?, ?)",
        (dataDict["AUD"], dataDict["BCH"], dataDict["BTC"], dataDict["ETC"], dataDict["ETH"], dataDict["LTC"], dataDict["TIME"], dataDict["XRP"]))

        conn.commit()
        conn.close()
    except Exception as inst:
        print(inst)

def main():
    res = build_headers(uri, pkey, skey)
    r = requests.get(domain+uri, headers=res, verify=True)

    if len(r.json()) == 7:
        dataDict["TIME"] = time.time()
        for i in r.json():
            dataDict[i["currency"]] = int(i["balance"])/100000000

        print(dataDict)
        WriteToDb()
    else:
        print(r.json())

    # Now get trading fee
    luri = "/account/BTC/AUD/tradingfee"
    res = build_headers(luri, pkey, skey)
    r = requests.get(domain+luri, headers=res, verify=True)
    print(r.json())

if __name__ == "__main__":
    main()