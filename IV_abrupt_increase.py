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
    return iv[-1]["value"],iv[-2]["value"]

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
    return iv[-1]["value"],iv[-2]["value"]

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


abrupt_increase_list = list()
def detect_volatility_increase(ticker="AAPL"):
    """
    Calculate avg volatiliy
    :param ticker:  ticker name
    :param lookahead: lookahead
    :return:
    """
    print(ticker)
    s = Stock(ticker)
    global abrupt_increase_list
    if get_volume(ticker)>5000000 and s.price>10:
        ivput_now, ivput_past= get_volatility_put(ticker)
        ivcall_now,ivcall_past = get_volatility_call(ticker)
    # get the most recent values
        if  ivput_now>1.3*ivput_past and ivput_now>0.3:
            #s = Stock(ticker)
            #if get_volume(ticker) > 1000000 and s.price>10:
            print(ticker, "has abrupt increase in volatility")
            abrupt_increase_list.append(ticker)
        elif  ivcall_now>1.3*ivcall_past and ivcall_now>0.3:
            #s = Stock(ticker)
            #if get_volume(ticker) > 1000000 and s.price>10:
            print(ticker, "has abrupt increase in volatility")
            abrupt_increase_list.append(ticker)
        


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

start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(detect_volatility_increase,option_list)
print(abrupt_increase_list)
abrupt_increase_list = list()
# %%

    
    
    
