from yahoo_fin import options
import yfinance as yf
from wallstreet import Stock, Call, Put
import wallstreet
import csv
import urllib, json
from get_all_tickers import get_tickers as gt
from get_all_tickers.get_tickers import Region
import os.path
from os import path
import threading, multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
from itertools import zip_longest
import concurrent.futures
from time import time

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
    print(udlying)
    if s.price > min_price and s.price < max_price:
        filtered_list.append(udlying)

def price_filter_multi(list_of_tickers):
    processes=[]
    with ThreadPoolExecutor(max_workers=100) as executor:
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
    resp = urllib.request.urlopen(url)
    iv = json.loads(resp.read())
    return iv

def get_avg_volatility(ticker="AAPL", lookahead=30):

    iv = get_volatility(ticker)
    # get the most recent values
    iv_lookahead = iv[-lookahead:]
    ivs = [k['value'] for k in iv_lookahead]
    for idx in range(len(ivs)):
        if ivs[idx] is None:
            ivs[idx] = 0
    iv_avg = sum(ivs) / lookahead
    return iv_avg, iv

def get_high_iv_list(ticker, threshold=0.8):
    avg, iv = get_avg_volatility(ticker)
    if avg > threshold:
        print(ticker, "meet the threshold")
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

if __name__ == "__main__":
    #option_list, _ = get_tickers()
    print('running')
    option_list = csv_read (csv_name="optionable_list.csv")
    #option_list = ['TXG', 'TURN', 'FLWS', 'ONEM', 'SRCE', 'VNET', 'TWOU', 'QFIN', 'JOBS', 'ETNB', 'EGHT', 'NMTR', 'AAON', 'ABEO', 'ABMD', 'AXAS', 'ACIU', 'ACIA', 'ACTG', 'ASO', 'ACHC', 'ACAD', 'AXDX', 'XLRN', 'ACCD', 'ARAY']
    price_filter_multi(option_list[1:1000])
    print(len(option_list))
    print(len(filtered_list))
    processes2 = []
    with ThreadPoolExecutor(max_workers=100) as executor:
       for ticker in filtered_list:
            processes2.append(executor.submit(get_high_iv_list, ticker))
    print(high_iv_list)
