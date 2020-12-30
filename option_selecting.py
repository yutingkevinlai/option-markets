from yahoo_fin import options
import yfinance as yf
from wallstreet import Stock, Call, Put
import wallstreet
import urllib, json
from get_all_tickers import get_tickers as gt
from get_all_tickers.get_tickers import Region
import os.path
from os import path

def GetInfo(udlying, day, month, year, stockprice, offset):
    u = Call(udlying, d=day, m=month, y=year, strike=stockprice+offset)
    price = u.price
    IV = u.implied_volatility()
    v = u.vega()
    g = u.gamma()
    strike = u.strike
    return (IV,v,g,price,strike)

def moves(DTern,DTE,IV,IVn,v,g,price_move,offset):
    IV_AE = ((DTern/(DTern+DTE))*IV**2 + (DTE/(DTern+DTE))*IVn**2)**0.5
    vega_change = v*(IV_AE-IV)*100
    gamma_change = 0.5*g*(price_move+offset)**2
    return (IV_AE,vega_change,gamma_change)

def get_tickers():
    list_of_tickers = gt.get_tickers_by_region(Region.NORTH_AMERICA)
    print(list_of_tickers[3])
    print(len(list_of_tickers))
    optionable_list = []
    filtered_list = []
    minPrice = 20
    maxPrice = 50
    for stock_idx in range(1,20):
        udlying = list_of_tickers[stock_idx]
        print(stock_idx, udlying)
        g = options.get_expiration_dates(udlying)
        if len(g) != 0:
            optionable_list.append(udlying)
            s = Stock(list_of_tickers[stock_idx])
            if s.price > minPrice and s.price < maxPrice:
                filtered_list.append(list_of_tickers[stock_idx])
    print(optionable_list)
    with open('optionable_list.txt', 'w') as f:
        for item in optionable_list:
            f.write("%s\n" % item)
    # print(len(optionable_list))
    # print(filtered_list)
    # print(len(filtered_list))
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

def get_high_iv_list(option_list, threshold=0.8):
    high_iv_list = []
    for k in range(len(option_list)):
        ticker = option_list[k]
        print(ticker)
        iv = get_volatility(ticker)
        avg = get_avg_volatility(ticker)
        print(avg)
        if avg > threshold:
            high_iv_list.append(ticker)
    return high_iv_list

if __name__ == "__main__":
    option_list, _ = get_tickers()
    # option_list = ['TXG', 'TURN', 'FLWS', 'ONEM', 'SRCE', 'VNET', 'TWOU', 'QFIN', 'JOBS', 'ETNB', 'EGHT', 'NMTR', 'AAON', 'ABEO', 'ABMD', 'AXAS', 'ACIU', 'ACIA', 'ACTG', 'ASO', 'ACHC', 'ACAD', 'AXDX', 'XLRN', 'ACCD', 'ARAY']
    high_iv_list = get_high_iv_list(option_list)
    print(high_iv_list)
