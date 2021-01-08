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

optionable_list = []
filtered_list = []
IV_increasing_list = []
min_price = 30
max_price = 200


# %%


def get_volume(ticker="AAPL"):
    """
    Get stock's volume
    :param ticker: ticker name
    :return:
    """
    url = "https://www.alphaquery.com/data/stock-price-chart"
    params = {
        "ticker": ticker,
    }
    r = requests.get(url=url, params=params)
    stock_info = r.json()
    volume = stock_info["adjusted"][-1]["volume"]
    return volume

def get_tickers():
    """
    Get available tickers
    :return: optionable_list, filtered_list
    """

    global filtered_list

    ## read all ticker names
    list_of_tickers = csv_read(csv_name="all_tickers_V2.csv")
    print(list_of_tickers)
    print(len(list_of_tickers))

    ## find all available tickers
    start = time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(find_optionable_stocks, list_of_tickers)

    print(optionable_list)
    print(filtered_list)

    ## write back the results to text
    with open('optionable_list.txt', 'w') as f:
        for item in optionable_list:
            f.write("%s\n" % item)
    # print(len(optionable_list))
    # print(filtered_list)
    # print(len(filtered_list))
    print(f'Time taken: {time() - start}')

    return optionable_list, filtered_list

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

def get_stock(ticker="AAPL"):
    """
    Get stock info
    :param ticker: ticker name
    :return: stock info
    """
    url = f"https://query1.finance.yahoo.com/v7/finance/options/{ticker}"
    # params = {
    #     "ticker": ticker,
    # }
    r = requests.get(url=url)
    print(r)
    stock = r.json()
    return stock

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

def volume_filter(udlying, v_min=5000000):
    """
    filter stock volume
    :add to filtered_list
    :param udlying: stock
    :param v_min: volume threshold
    :return: None
    """
    global filtered_list
    #print(udlying)
    if get_volume(udlying)>v_min:
        filtered_list.append(udlying)

def get_high_iv_and_filter_volume(ticker,threshold=0.5,v_min=5000000):
    global filtered_list

    if get_volatility_10day(ticker) >max(threshold,get_volatility(ticker)) and get_volume(ticker) > v_min:
        print(f"Add {ticker}")
        filtered_list.append(ticker)


def price_filter(udlying, min_price = 30, max_price = 200):
    """
    filter price between min and max
    add filtered price to filtered_list
    :param udlying: stock
    :param min_price: min price default 30
    :param max_price: max price dafult 200
    :return: None
    """
    global filtered_list
    s = Stock(udlying)
    if min_price < s.price < max_price:
        filtered_list.append(udlying)

def price_filter_multi(list_of_tickers):
    """
    filter prices with multi-threads

    :param list_of_tickers: list of tickers
    :return: None

    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        executor.map(price_filter, list_of_tickers)

def volume_filter_multi(list_of_tickers):
    """
    filter prices with multi-threads

    :param list_of_tickers: list of tickers
    :return: None

    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        executor.map(volume_filter, list_of_tickers)

# %%

def DTE(expiration):
    """
    Find DTE from expiration
    :param expiration: expiration time (int)
    :return: number of days
    """
    exp_date = date(int(expiration[0:4]), int(expiration[5:7]), int(expiration[8:10]) + 1)
    today = date.today()
    delta = exp_date - today
    return (delta.days)

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
#%%
def multi_find_score_multiprocess(udlying,processes=None):
    print(udlying)
    ticker = yf.Ticker(udlying)
    expirations = ticker.options ## yfinance libarary
    #print(expirations)
    if not processes:
        with multiprocessing.Pool(processes=processes) as pool:
            results = pool.map(partial(find_score_each_expiration, udlying=udlying), expirations[:5])
            print(print("Best option overall:", max(results)[1]))
    else:
        with multiprocessing.Pool() as pool:
            results = pool.map(partial(find_score_each_expiration, udlying=udlying), expirations[:5])
            print(print("Best option overall:", max(results)[1]))

def Refilter_input(refilter=False):
    global filtered_list
    if refilter:
        print("refiltering lists")
        option_list = csv_read (csv_name="optionable_list.csv")
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(get_high_iv_and_filter_volume,option_list)
        np.savetxt("filtered_list.csv", filtered_list, delimiter=",", fmt="%s")
    filtered_list = list()

# %%

# if __name__ == '__main__':
print('running')
print('reading input')
Refilter_input(refilter=False)
input_list = csv_read (csv_name="filtered_list.csv")



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
    
