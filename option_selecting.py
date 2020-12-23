from yahoo_fin import options
import yfinance as yf
from wallstreet import Stock, Call, Put
import wallstreet
from get_all_tickers import get_tickers as gt
from get_all_tickers.get_tickers import Region

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


list_of_tickers = gt.get_tickers_by_region(Region.NORTH_AMERICA)
print(list_of_tickers[3])
print(len(list_of_tickers))
optionable_list = []
filteredList = []
minPrice = 20
maxPrice = 50
for stock_idx in range(1,50):
    udlying = list_of_tickers[stock_idx]
    print(stock_idx, udlying)
    g = options.get_expiration_dates(udlying)
    if len(g) != 0:
        optionable_list.append(udlying)
        s = Stock(list_of_tickers[stock_idx])
        if s.price > minPrice and s.price < maxPrice:
            filteredList.append(list_of_tickers[stock_idx])
print(optionable_list)
print(len(optionable_list))

print(filteredList)
print(len(filteredList))
