

import numpy as np
from cookies import *

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

def find_best_option(ticker = "AAPL"):
    ticker = "NIO"
    option_info = get_option_chain_barchart(ticker = ticker)
    expirations_raw = option_info["meta"]["expirations"]
    expirations = {}
    for key, value in expirations_raw.items():
        for v in value:
            expirations[v] = key
    web_access =0
    max_score = 0
    idx_rec = list()
    clstype = "Put"
    for expi in expirations:
        Date_to_expire = DTE(expi)
        if(Date_to_expire>60) or Date_to_expire==0:
            continue
        web_access+=1
        option_info = get_option_chain_barchart(ticker = ticker, expi=expi, Type = expirations[expi])
        puts_info =option_info["data"][clstype] 
        for i in puts_info:
            opt_strike = i['raw']["strikePrice"]
            opt_price = i['raw']["lastPrice"]
            opt_theo_price = i['raw']["theoretical"]
            opt_delta = i['raw']["delta"]
            opt_gamma = i['raw']["gamma"]
            opt_theta = i['raw']["theta"]
            opt_vega = i['raw']["vega"]
            opt_DTE = i['raw']["daysToExpiration"]
            RoR = opt_price/opt_strike
            if abs(opt_delta) > 0.5 or abs(opt_delta) < 0.1 or RoR < 0.005:
                break
            K1 = 30 / (opt_DTE+1)
            score = K1 * (1 - 2.5 * abs(opt_delta)) * opt_theo_price * 2000 / opt_strike
            if score > max_score:
                max_score = score
                idx_rec = [ticker, expi, opt_strike, clstype, "with score:", score]
            #print(opt_strike, opt_delta, score, RoR)
#listToStr = ' '.join(map(str, idx_rec)) 
#print(listToStr)
    print(web_access)
    return idx_rec

find_best_option()     
