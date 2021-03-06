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
from Dev.cookies import get_option_chain_barchart
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
        
def find_best_option(ticker="AAPL", Only_monthly = False):
    ## switching to barchart for scrapping data with more strucutred option chain data
    print("finding best option for:", ticker)
    option_info = get_option_chain_barchart(ticker = ticker)
    if option_info.get('error'):
        print("Too many attempts, resting 10 sec")
        time.sleep(10)
        option_info = get_option_chain_barchart(ticker = ticker)

    expirations_raw = option_info["meta"]["expirations"]

    
    expirations = {}
    idx_rec = ["no option found"]
    clstype = "Put"
    ## reorganize the expiration data for formats when accessing barchart
    if len(expirations_raw)==0:
        return idx_rec
    for key, value in expirations_raw.items():
        if Only_monthly is True and key == 'weekly':
            continue
        for v in value:
            expirations[v] = key
    
    max_score = 0
    
    for expi in expirations:
        Date_to_expire = DTE(expi)  ## find date to expiration
        if(Date_to_expire>50) or Date_to_expire==0: ## continue the loop if expiration date is too far away
            continue
        option_info = get_option_chain_barchart(ticker = ticker, expi=expi, Type = expirations[expi])
        if option_info.get('error'):
            print("Too many attempts, resting 10 sec")
            time.sleep(10)
            option_info = get_option_chain_barchart(ticker = ticker, expi=expi, Type = expirations[expi])
        puts_info =option_info["data"][clstype] 
        for i in puts_info: ## iterate all the strike prices
            opt_strike = i['raw']["strikePrice"]            
            opt_price = (2*i['raw']["lastPrice"]+i['raw']["bidPrice"]+i['raw']["askPrice"])/4
            opt_theo_price = i['raw']["theoretical"]
            opt_delta = i['raw']["delta"]
            RoR = opt_price/opt_strike
            if abs(opt_delta) > 0.5:
                break ## filter out in-the-money option, small RoR or small delta options 
            if abs(opt_delta) < 0.1 or RoR < 0.005:
                continue
            opt_gamma = i['raw']["gamma"]
            opt_theta = i['raw']["theta"]
            opt_vega = i['raw']["vega"]
            opt_DTE = i['raw']["daysToExpiration"]
            

            K1 = 30 / (opt_DTE+1)
            
            #### finding score here
            score = K1 * (1 - 2.5 * abs(opt_delta)) * opt_price * 2000 / opt_strike
            
            
            if score > max_score: ## comparing the scores
                max_score = score
                idx_rec = [ticker, expi, opt_strike, clstype, "with score:", score, "theo_price:", opt_theo_price, "last_price:",i['raw']["lastPrice"]]
        time.sleep(0.5) ## reduce access time of the website
    listToStr = ' '.join(map(str, idx_rec)) 
    print(listToStr)
    return idx_rec

# %%



# %%

# if __name__ == '__main__':
print('running')
print('reading input')
Refilter_input(refilter=False)
input_list = read_file(csv_name="filtered_list.csv")
input_list.remove('IPOC')


print(input_list)
# %%
#Multithreads

for ticker in input_list:
    pd.options.mode.chained_assignment = None  # default='warn'
    find_best_option(ticker=ticker, Only_monthly = True)
