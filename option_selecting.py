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

def get_high_iv_list(ticker, threshold=0.8):
    """
    Add ticker larger than threshold to high_iv_list
    :param ticker: stock name
    :param threshold: threshold int
    :return: high_iv_list(list)
    """
    global high_iv_list
    avg, iv = get_avg_volatility(ticker)
    # print(avg)
    if avg > threshold:
        # print(ticker, "meet the threshold")
        high_iv_list.append(ticker)
        #with open(f"{ticker}.json", 'w') as outfile:
        #    json.dump(iv, outfile)
    return high_iv_list

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

def get_high_iv_and_filter_volume(ticker,threshold=0.8,v_min=5000000):
    global filtered_list

    avg, iv = get_avg_volatility(ticker)
    if avg > threshold and get_volume(ticker) > v_min:
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

def find_score(expiration, premium, delta, strike):
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
    score = K1 * (1 - 3 * abs(delta)) * premium * 2000 / strike
    return score

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
        option = Put(udlying, d=int(expiration[8:10])+1, m=int(expiration[5:7]), y=int(expiration[0:4]), strike=strike)
        premium = (2*option.price+option.bid+option.ask)/4
        delta = option.delta()
        score = int(find_score(expiration, premium, delta, strike))
        #print(expiration, "on", udlying, float(strike), "put has a score", int(score))
        if abs(delta) < 0.1 or  premium<0.025*strike:
            return Best_option_score,Best_option
        if score > Best_option_score:
            Best_option_score = score
            Best_option = "{} {} {} put with score {}.{}".format(udlying, expiration, float(strike), int(score),int(delta))

def multi_find_score(udlying):
    """
    :param udlying:
    :return:
    """
    expirations = get_expiration(ticker=udlying)
    #print(expirations)
    results = list()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for expi in expirations[:2]:
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



# %%

# if __name__ == '__main__':
print('running')
print('reading input')
option_list = csv_read (csv_name="optionable_list.csv")

#%%

# print('price filtering')
# price_filter_multi(option_list[1:1000])
# print(len(option_list))
# print(len(filtered_list))

#print('finding high IV stocks')

#with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
#    executor.map(get_high_iv_list,option_list)
#print(high_iv_list)

#%%
#print("volume filtering")
#volume_filter_multi(high_iv_list)
#print(filtered_list)
#pd.options.mode.chained_assignment = None  # default='warn'

#%%
#Combine the two function above

start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(get_high_iv_and_filter_volume,option_list)
print(filtered_list)

# %%
#Multithreads
for udlying in filtered_list:
    pd.options.mode.chained_assignment = None  # default='warn'
    print('finding the best option for', udlying)
    multi_find_score(udlying)
    
print(f"Threads Time: {time.time()-start}")
filtered_list=list()
    
    
    
