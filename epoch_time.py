# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 16:54:49 2021

@author: a0937
"""

import time
import requests


def get_expiration(ticker="AAPL",time_diff=1):
    """
    Get stock info
    :param ticker: ticker name
    :param time_diff: time difference
    :return: stock info
    """
    url = f"https://query1.finance.yahoo.com/v7/finance/options/{ticker}"
    # params = {
    #     "ticker": ticker,
    # }
    DAY = 86400*time_diff
    r = requests.get(url=url)
    stock = r.json()
    epoch_dates = stock.get("optionChain",{}).get("result",[])[0].get("expirationDates",None)
    expirations = [time.strftime('%Y-%m-%d', time.localtime(date+DAY)) for date in epoch_dates]
    return expirations


test = get_expiration()

print(test)