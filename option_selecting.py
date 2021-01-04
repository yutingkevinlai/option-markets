# %%
import urllib, json
import multiprocessing, threading
import pandas as pd
import concurrent.futures
from functools import partial
from time import time
from datetime import date
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from yahoo_fin import options
import yfinance as yf
from wallstreet import Stock, Call, Put

from Utility.stock_utility import *

optionable_list = []
filtered_list = []
high_iv_list = []
min_price = 30
max_price = 200


# %%
# Function

# def find_optionable_stocks(udlying):
#     g = options.get_expiration_dates(udlying)
#     print(udlying)
#     if len(g) != 0:
#         print(udlying, "has options")
#         optionable_list.append(udlying)

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
    stock = r.json()
    return stock

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
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(price_filter, list_of_tickers)


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


# def get_volatility(ticker="AAPL"):
#     url_1 = "https://www.alphaquery.com/data/option-statistic-chart?ticker="
#     url_2 = "&perType=30-Day&identifier=iv-call"
#     url = url_1 + ticker + url_2
#     #print(url)
#     resp = urllib.request.urlopen(url)
#     iv = json.loads(resp.read())
#     return iv

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
        "identifier": "iv-call"
    }
    r = requests.get(url=url, params=params)
    iv = r.json()
    return iv

# %%
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


# def find_delta (ticker,dates,strike):
#     u = put(udlying, d=15, m=1, y=2021, strike=stockprice+offset)
#     score=2*delta-1
#     price = u.price
#     return content


# @contextmanager
# def poolcontext(*args, **kwargs):
#     pool = multiprocessing.Pool(*args, **kwargs)
#     yield pool
#     pool.terminate()


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
    score = K1 * (1 - 2 * abs(delta)) * premium * 2000 / strike
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
        print(expiration, "on", udlying, float(strike), "put has a score", int(score))
        if score > Best_option_score:
            Best_option_score = score
            Best_option = "{} {} {} put with score {}.".format(udlying, expiration, float(strike), int(score))
        
        if abs(delta) < 0.1 or  premium<0.1*strike:
            return Best_option_score,Best_option


def multi_find_score(udlying):
    """
    :param udlying:
    :return:
    """
    print(udlying)
    ticker = yf.Ticker(udlying)
    expirations = ticker.options
    print(expirations)
    results = list()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for expi in expirations[:5]:
            futures.append(executor.submit(partial(find_score_each_expiration, udlying=udlying), expi))

        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    res = filter(None, results)
    if res:
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
# print('running')
# print('reading input')
# option_list = csv_read (csv_name="optionable_list.csv")
# print('price filtering')
# price_filter_multi(option_list[1:1000])
# print(len(option_list))
# print(len(filtered_list))
# print('finding high IV stocks')
# processes2 = []
# with ThreadPoolExecutor(max_workers=100) as executor:
#   for ticker in filtered_list:
#        processes2.append(executor.submit(get_high_iv_list, ticker))
# print(high_iv_list)
# udlying = high_iv_list[0]

ticker = "PLTR"
r = get_stock(ticker)
print(r)

udlying = "PLTR"
print(udlying)
>>>>>>> 32045376f195635fc4d5d7bc93213c972e3882fc
pd.options.mode.chained_assignment = None  # default='warn'
print('finding the best option')

# %%
## Multithreads
start = time()
multi_find_score(udlying)
print(f"Multithreads: {time() - start}")
# %%
## multiprocess
start = time()
multi_find_score_multiprocess(udlying)
print(f"multiprocess: {time() - start}")
