
import multiprocessing
from functools import partial
from contextlib import contextmanager
from yahoo_fin import options
import yfinance as yf
from wallstreet import Stock, Call, Put
import wallstreet
import csv
import urllib, json
import os.path
from os import path
import threading, multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
from itertools import zip_longest
import concurrent.futures
from time import time
import pandas as pd
import math
from datetime import date

optionable_list = []
filtered_list = []
high_iv_list = []
min_price = 30
max_price = 200

def find_optionable_stocks(udlying):
    g = options.get_expiration_dates(udlying)
    print(udlying)
    if len(g) != 0:
        print(udlying, "has options")
        optionable_list.append(udlying)

def price_filter(udlying):
    s = Stock(udlying)
    if s.price > min_price and s.price < max_price:
        filtered_list.append(udlying)
        
def price_filter_multi(list_of_tickers):
    processes=[]
    with ThreadPoolExecutor(max_workers=5) as executor:
        for udlying in list_of_tickers:
            processes.append(executor.submit(price_filter, udlying))

def get_tickers():
    list_of_tickers = csv_read(csv_name="all_tickers_V2.csv")
    print(list_of_tickers)
    print(len(list_of_tickers))
    processes = []
    start = time()
    with ThreadPoolExecutor(max_workers=5) as executor:
        for udlying in list_of_tickers:
            processes.append(executor.submit(find_optionable_stocks, udlying))
    print(optionable_list)
    print(filtered_list)
    with open('optionable_list.txt', 'w') as f:
        for item in optionable_list:
            f.write("%s\n" % item)
    # print(len(optionable_list))
    # print(filtered_list)
    # print(len(filtered_list))
    print(f'Time taken: {time() - start}')
    return optionable_list, filtered_list

def get_volatility(ticker="AAPL"):
    url_1 = "https://www.alphaquery.com/data/option-statistic-chart?ticker="
    url_2 = "&perType=30-Day&identifier=iv-call"
    url = url_1 + ticker + url_2
    #print(url)
    resp = urllib.request.urlopen(url)
    iv = json.loads(resp.read())
    return iv

def get_avg_volatility(ticker="AAPL", lookahead=30):

    iv = get_volatility(ticker)
    # get the most recent values
    iv_lookahead = iv[-lookahead:]
    #print(len(iv_lookahead))
    ivs = [k['value'] for k in iv_lookahead]
    for idx in range(len(ivs)):
        if ivs[idx] is None:
            ivs[idx] = 0

    iv_avg = sum(ivs) / lookahead
    return iv_avg, iv

def get_high_iv_list(ticker, threshold=0.8):
    #print(ticker)
    avg, iv = get_avg_volatility(ticker)
    #print(avg)
    if avg > threshold:
        #print(ticker, "meet the threshold")
        high_iv_list.append(ticker)
        with open(ticker+'.json', 'w') as outfile:
            json.dump(iv, outfile)
    return high_iv_list

def csv_read (csv_name="all_tickers.csv"):
    content = []
    with open(csv_name, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for lines in csv_reader:
            content.append(lines[0])
    return content

def find_delta (ticker,dates,strike):
    u = put(udlying, d=15, m=1, y=2021, strike=stockprice+offset)
    score=2*delta-1
    price = u.price
    return content


@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()

    
def DTE(expiration):
    exp_date = date(int(expiration[0:4]), int(expiration[5:7]), int(expiration[8:10])+1)
    today = date.today()
    delta = exp_date - today
    return (delta.days)
    
def find_score(expiration,premium,delta,strike):
    time_diff = DTE(expiration)
    K1 = 30/time_diff
    score = K1*(1-2*abs(delta))*premium*2000/strike
    return score

def find_score_each_expiration(expiration,udlying):
    ticker = yf.Ticker(udlying)
    opt = ticker.option_chain(expiration)
    df = opt.puts
    s_array = df[["strike","inTheMoney"]]
    indexNames = s_array[ (s_array['inTheMoney'] == True) ].index
    s_array.drop(indexNames , inplace=True)
    df=[]
    strikes=s_array[["strike"]].to_numpy()[::-1]
    Best_option_score = 0
    Best_option = []
    if len(strikes)==0:
        return Best_option_score,Best_option   
    for strike in strikes:
        option = Put(udlying, d=int(expiration[8:10]), m=int(expiration[5:7]), y=int(expiration[0:4]), strike=strike)
        premium = (2*option.price+option.bid+option.ask)/4
        delta = option.delta()
        score = int(find_score(expiration,premium,delta,strike))
        #print(expiration, "on",udlying, float(strike),"put has a score", int(score))
        if score > Best_option_score:
            Best_option_score = score
            Best_option = "{} {} {} put with score {}.".format(udlying, expiration, float(strike), int(score))
        
        if abs(delta) < 0.1 or  premium<0.02*strike:
            return Best_option_score,Best_option
    


def multi_find_score (udlying):
    print(udlying)
    ticker = yf.Ticker(udlying)
    expirations = ticker.options
    print(expirations)
    with poolcontext(processes=5) as pool:
        results = pool.map(partial(find_score_each_expiration, udlying=udlying), expirations[0:5])
    print("Best option overall:",max(results)[1])


if __name__ == '__main__':
    #print('running')
    #print('reading input')
    #option_list = csv_read (csv_name="optionable_list.csv")
    #print('price filtering')
    #price_filter_multi(option_list[1:1000])
    #print(len(option_list))
    #print(len(filtered_list))
    #print('finding high IV stocks')
    #processes2 = []
    #with ThreadPoolExecutor(max_workers=100) as executor:
    #   for ticker in filtered_list:
    #        processes2.append(executor.submit(get_high_iv_list, ticker))
    #print(high_iv_list)
    #udlying = high_iv_list[0]
    udlying="PLTR"
    print(udlying)
    pd.options.mode.chained_assignment = None  # default='warn'
    print('finding the best option')
    multi_find_score(udlying)
