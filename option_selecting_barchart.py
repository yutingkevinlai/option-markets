# %%
import urllib, json
import multiprocessing, threading
import pandas as pd
import concurrent.futures
from functools import partial
from time import time
from datetime import date

import requests
from yahoo_fin import options
import yfinance as yf
from wallstreet import Stock, Call, Put
import time 
import numpy as np

from Utility.stock_utility import *
from option_selecting import price_filter, volume_filter, get_high_iv_and_filter_volume, \
    price_filter_multi, volume_filter_multi, DTE, multi_find_score_multiprocess, Refilter_input

optionable_list = []
filtered_list = []
IV_increasing_list = []
min_price = 30
max_price = 200


# %%

def get_volatility(ticker="AAPL"):
    """
    Get stock's volatiliy
    :param ticker: ticker name
    :return: list of json volatility data
    """
    url = "https://www.alphaquery.com/data/option-statistic-chart"
    params = {
        "ticker": ticker,
        "perType": "30-Day",
        "identifier": "iv-put"
    }
    r = requests.get(url=url, params=params)
    iv = r.json()
    return iv[-1]['value']

def get_volatility_10day(ticker="AAPL"):
    """
    Get stock's volatiliy
    :param ticker: ticker name
    :return: list of json volatility data
    """
    url = "https://www.alphaquery.com/data/option-statistic-chart"
    params = {
        "ticker": ticker,
        "perType": "10-Day",
        "identifier": "iv-put"
    }
    r = requests.get(url=url, params=params)
    iv = r.json()
    return iv[-1]['value']



def get_IV_increasing_list(ticker):
    """
    Add ticker with 10day put IV larger than 30 day put IV 
    :param ticker: stock name
    :param threshold: threshold int
    :return: high_iv_list(list)
    """
    global IV_increasing_list
    if get_volatility_10day(ticker) > get_volatility(ticker):
        # print(ticker, "meet the threshold")
        IV_increasing_list(ticker)
        #with open(f"{ticker}.json", 'w') as outfile:
        #    json.dump(iv, outfile)
    return IV_increasing_list

def get_high_iv_and_filter_volume(ticker,threshold=0.8,v_min=5000000):
    global filtered_list

    avg, iv = get_avg_volatility(ticker)
    if avg > threshold and get_volume(ticker) > v_min:
        print(f"Add {ticker}")
        filtered_list.append(ticker)
        
def Refilter_input(refilter=False):
    global filtered_list
    if refilter:
        print("refiltering lists")
        option_list = read_file(csv_name="optionable_list.csv")
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(get_high_iv_and_filter_volume,option_list)
        np.savetxt("filtered_list.csv", filtered_list, delimiter=",", fmt="%s")
    filtered_list = list()
   
    
def find_best_option(ticker = "AAPL"):
    print("finding best option for:", ticker)
    option_info = get_option_chain_barchart(ticker = ticker)
    expirations_raw = option_info["meta"]["expirations"]
    expirations = {}
    for key, value in expirations_raw.items():
        for v in value:
            expirations[v] = key
    
    max_score = 0
    idx_rec = ["no option found"]
    clstype = "Put"
    for expi in expirations:
        Date_to_expire = DTE(expi)
        if(Date_to_expire>60) or Date_to_expire==0:
            continue
        option_info = get_option_chain_barchart(ticker = ticker, expi=expi, Type = expirations[expi])
        puts_info =option_info["data"][clstype] 
        for i in puts_info:
            opt_strike = i['raw']["strikePrice"]
            opt_price = i['raw']["lastPrice"]
            opt_theo_price = i['raw']["theoretical"]
            opt_delta = i['raw']["delta"]
            opt_gamma = i['raw']["gamma"]
            opt_theta = i['raw']["theta"]
            opt_vega = i['raw']["vega"]
            opt_DTE = i['raw']["daysToExpiration"]
            RoR = opt_price/opt_strike
            if opt_DTE>60 or abs(opt_delta) > 0.5 or abs(opt_delta) < 0.1 or RoR < 0.005:
                break
            K1 = 30 / (opt_DTE+1)
            score = K1 * (1 - 2.5 * abs(opt_delta)) * opt_theo_price * 2000 / opt_strike
            if score > max_score:
                max_score = score
                idx_rec = [ticker, expi, opt_strike, clstype, "with score:", score]
            #print(opt_strike, opt_delta, score, RoR)
    listToStr = ' '.join(map(str, idx_rec)) 
    print(listToStr)
    return idx_rec

def multi_find_score(ticker = "AAPL"):

    return 
# %%



# %%

# if __name__ == '__main__':
print('running')
print('reading input')
Refilter_input(refilter=False)
input_list = read_file(csv_name="filtered_list.csv")



print(input_list)

# %%
#Multithreads

for ticker in input_list:
    pd.options.mode.chained_assignment = None  # default='warn'
    find_best_option(ticker=ticker)
    time.sleep(1)
