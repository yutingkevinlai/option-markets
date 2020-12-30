from yahoo_fin import options
import yfinance as yf
from wallstreet import Stock, Call, Put
import wallstreet
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
min_price = 0
max_price = 10000

def find_optionable_stocks(udlying):
    g = options.get_expiration_dates(udlying)
    if len(g) != 0:
        optionable_list.append(udlying)
        s = Stock(udlying)
        if s.price > min_price and s.price < max_price:
            filtered_list.append(udlying)

def get_tickers():
    list_of_tickers = gt.get_tickers_by_region(Region.NORTH_AMERICA)
    print(len(list_of_tickers))
    processes = []
    start = time()
    with ThreadPoolExecutor(max_workers=100) as executor:
        for udlying in list_of_tickers[1:100]:
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
    print(url)
    resp = urllib.request.urlopen(url)
    iv = json.loads(resp.read())
    with open(ticker+'.json', 'w') as outfile:
        json.dump(iv, outfile)
    return iv

def get_avg_volatility(ticker="AAPL", lookahead=30):
    filename = ticker + '.json'
    if path.exists(filename):
        with open(ticker+'.json') as f:
            iv = json.load(f)
    else:
        iv = get_volatility(ticker)
    # get the most recent values
    iv_lookahead = iv[-lookahead:]
    print(len(iv_lookahead))
    ivs = [k['value'] for k in iv_lookahead]
    for idx in range(len(ivs)):
        if ivs[idx] is None:
            ivs[idx] = 0

    iv_avg = sum(ivs) / lookahead
    return iv_avg

def get_high_iv_list(ticker, threshold=0.8):
    print(ticker)
    iv = get_volatility(ticker)
    avg = get_avg_volatility(ticker)
    print(avg)
    if avg > threshold:
        high_iv_list.append(ticker)
    return high_iv_list

if __name__ == "__main__":
    option_list, _ = get_tickers()
    #option_list = ['TXG', 'TURN', 'FLWS', 'ONEM', 'SRCE', 'VNET', 'TWOU', 'QFIN', 'JOBS', 'ETNB', 'EGHT', 'NMTR', 'AAON', 'ABEO', 'ABMD', 'AXAS', 'ACIU', 'ACIA', 'ACTG', 'ASO', 'ACHC', 'ACAD', 'AXDX', 'XLRN', 'ACCD', 'ARAY']
    processes2 = []   
    with ThreadPoolExecutor(max_workers=100) as executor:
        for ticker in option_list:
            processes2.append(executor.submit(get_high_iv_list, ticker))
    print(high_iv_list)
