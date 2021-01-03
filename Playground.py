

import requests
from time import time
def get_volatility(ticker="AAPL"):
    url = "https://www.alphaquery.com/data/option-statistic-chart"
    params = {
        "ticker" : ticker,
        "perType" : "30-Day",
        "identifier" : "iv-call"
    }
    r = requests.get(url=url,params=params)
    iv = r.json()
    return iv


# iv = get_volatility()
#
# print(iv)

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
    #print(len(iv_lookahead))


    start = time()
    ivs = [k['value']  if k['value'] else 0.0 for k in iv_lookahead]

    iv_avg = sum(ivs) / lookahead

    print(f"time is {time()-start}")
    return iv_avg, iv

iv_avg, iv = get_avg_volatility()
print(iv_avg)