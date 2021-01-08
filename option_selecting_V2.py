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



# %%


def find_score(expiration, premium, delta,gamma,theta, strike):
    """
    find score
    :param expiration:
    :param premium:
    :param delta:
    :param strike:
    :return:
    """
    time_diff = DTE(expiration)
    K1 = 30 / time_diff
    K2 = theta/gamma
    if K2 < 1:
        score = 0
        return score, K2
    score = (K2**0.5) * K1 * (1 - 2.5 * abs(delta)) * premium * 1000 / strike
    return score, K2

def find_score_each_expiration(expiration, udlying):
    """

    :param expiration:
    :param udlying:
    :return:
    """
    #print(f"Processing {udlying}")
    ticker = yf.Ticker(udlying)
    opt = ticker.option_chain(expiration)
    df = opt.puts
    s_array = df[["strike", "inTheMoney"]]
    indexNames = s_array[(s_array['inTheMoney'] == True)].index
    s_array.drop(indexNames, inplace=True)
    df = []
    strikes = s_array[["strike"]].to_numpy()[::-1]
    Best_option_score = 0
    Best_option = []
    if len(strikes) == 0:
        return Best_option_score, Best_option
    for strike in strikes:
        option = Put(udlying, d=int(expiration[8:10]), m=int(expiration[5:7]), y=int(expiration[0:4]), strike=strike)
        premium = (2*option.price+option.bid+option.ask)/4
        delta = option.delta()
        gamma = option.gamma()
        theta = option.theta()
        score,K2 = find_score(expiration, premium, delta,gamma,theta, strike)
        #print(expiration, "on", udlying, float(strike), "put has a score", int(score),float(K2))
        if abs(delta) < 0.1 or  premium<0.025*strike or DTE(expiration)>50:
            return Best_option_score,Best_option
        if int(score) > Best_option_score:
            Best_option_score = score
            Best_option = "{} {} {} put with score: {} price:{:10.3f} tg ratio=:{:10.2f}.".format(udlying, expiration, float(strike), int(score),float(premium),float(K2))

def multi_find_score(udlying):
    """
    :param udlying:
    :return:
    """
    expirations = get_expiration(ticker=udlying,time_diff=1)
    #print(expirations)
    results = list()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for expi in expirations:
            futures.append(executor.submit(partial(find_score_each_expiration, udlying=udlying), expi))

        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    res = list(filter(None, results))
    if len(res)>0:
        print("Best option overall:",max(res)[1])

# %%

# if __name__ == '__main__':
print('running')
print('reading input')
Refilter_input(refilter=False)
input_list = read_file(csv_name="filtered_list.csv")



print(input_list)

# %%
#Multithreads

for udlying in input_list:
    pd.options.mode.chained_assignment = None  # default='warn'
    print('finding the best option for', udlying)
    multi_find_score(udlying)
    
   #option = Put("XPEV", d=19, m=2, y=2021, strike=40)
#delta = option.delta()
#gamma = option.gamma()
#theta = option.theta()
#K2 = theta/gamma
#print(delta,gamma,theta,K2) 
    
