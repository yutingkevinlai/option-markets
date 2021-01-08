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

from Utility.stock_utility import *

optionable_list = []
filtered_list = []
high_iv_list = []
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

def get_volatility_call(ticker="AAPL"):
    """
    Get stock's volatiliy
    :param ticker: ticker name
    :return: list of json volatility data
    """
    url = "https://www.alphaquery.com/data/option-statistic-chart"
    params = {
        "ticker": ticker,
        "perType": "30-Day",
        "identifier": "iv-call"
    }
    r = requests.get(url=url, params=params)
    iv = r.json()
    return iv

def get_volatility_put(ticker="AAPL"):
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
    return iv

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

def get_avg_volatility(ticker="AAPL", lookahead=30):
    """
    Calculate avg volatiliy
    :param ticker:  ticker name
    :param lookahead: lookahead
    :return:
    """

    iv = get_volatility(ticker)
    # get the most recent values
    iv_lookahead = iv[-lookahead:]
    # print(len(iv_lookahead))
    ivs = [k['value'] if k['value'] else 0.0 for k in iv_lookahead]

    iv_avg = sum(ivs) / lookahead
    return iv_avg, iv




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

High_IV_diff_list=list()
def High_IV_diff_flag(udlying):
    global High_IV_diff_list
    callIV = get_volatility_call(udlying)[-1]['value']
    putIV = get_volatility_put(udlying)[-1]['value']
    if abs(callIV-putIV)>0.5:
        print(udlying,"has large IV diff")
        s = Stock(udlying)
        if get_volume(udlying) > 1000000 and s.price>10:
            High_IV_diff_list.append(udlying)
            if callIV > putIV :
                print(udlying, "has call side skewed IV with req. met, diff",abs(callIV-putIV)) 
            elif putIV > callIV:
                print(udlying, "has put side skewed IV with req. met, diff",abs(callIV-putIV))
                
def High_IV_diff_flag_ratio(udlying):
    callIV = get_volatility_call(udlying)[-1]['value']
    putIV = get_volatility_put(udlying)[-1]['value']
    global High_IV_diff_list
    if callIV > 2*putIV :
        s = Stock(udlying)
        if get_volume(udlying) > 1000000 and s.price>10:
            High_IV_diff_list.append(udlying)
            print(udlying, "has call side skewed IV with req. met, ratio",callIV/putIV) 
    elif putIV > 2*callIV:
        s = Stock(udlying)
        if get_volume(udlying) > 1000000 and s.price>10:
            High_IV_diff_list.append(udlying)
            print(udlying, "has put side skewed IV with req. met, ratio",putIV/callIV)
# %%

# if __name__ == '__main__':
print('running')
print('reading input')
option_list = csv_read (csv_name="optionable_list.csv")

#%%
#print("volume filtering")
#volume_filter_multi(high_iv_list)
#print(filtered_list)
#pd.options.mode.chained_assignment = None  # default='warn'

#%%
#Combine the two function above
print("Finding put-call IV high diff stocks")
start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    #executor.map(High_IV_diff_flag_ratio,option_list)
    executor.map(High_IV_diff_flag,option_list)
print(High_IV_diff_list)

# %%

    
    
    
