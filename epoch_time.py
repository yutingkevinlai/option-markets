# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 16:54:49 2021

@author: a0937
"""

import time 


def get_expiration(ticker="AAPL"):
    """
    Get stock info
    :param ticker: ticker name
    :return: stock info
    """
    url = f"https://query1.finance.yahoo.com/v7/finance/options/{ticker}"
    # params = {
    #     "ticker": ticker,
    # }
    DAY = 86400
    r = requests.get(url=url)
    stock = r.json()
    Epoch_dates = stock['optionChain']['result'][0]['expirationDates']
    expirations = [time.strftime('%Y-%m-%d', time.localtime(i+DAY)) for i in Epoch_dates]
    return expirations


test = get_expiration()

print(test)