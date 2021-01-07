# %%
import concurrent.futures

from wallstreet import Stock, Call, Put

from Utility.stock_utility import *
from option_selecting import find_score_each_expiration

optionable_list = []
filtered_list = []
high_iv_list = []


# %%

def get_volatility_call(ticker="AAPL"):
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

def get_volatility_put(ticker="AAPL"):
    """
    Get stock's volatiliy
    :param ticker: ticker name
    :return: list of json volatility data
    """
    url = "https://www.alphaquery.com/data/option-statistic-chart"
    params = {
        "ticker": ticker,
        "perType": "30-Day",
        "identifier": "iv-put"
    }
    r = requests.get(url=url, params=params)
    iv = r.json()
    return iv


#%%

High_IV_diff_list=list()
def High_IV_diff_flag(udlying):
    callIV = get_volatility_call(udlying)[-1]['value']
    putIV = get_volatility_put(udlying)[-1]['value']
    if abs(callIV-putIV)>0.5:
        print(udlying,"has large IV diff")
        s = Stock(udlying)
        if get_volume(udlying) > 1000000 and s.price>10:
            High_IV_diff_list.append(udlying)
            if callIV > putIV :
                print(udlying, "has call side skewed IV with req. met, diff",abs(callIV-putIV)) 
            elif putIV > callIV:
                print(udlying, "has put side skewed IV with req. met, diff",abs(callIV-putIV))
                
def High_IV_diff_flag_ratio(udlying):
    callIV = get_volatility_call(udlying)[-1]['value']
    putIV = get_volatility_put(udlying)[-1]['value']
    if callIV > 2*putIV :
        s = Stock(udlying)
        if get_volume(udlying) > 1000000 and s.price>10:
            High_IV_diff_list.append(udlying)
            print(udlying, "has call side skewed IV with req. met, ratio",callIV/putIV) 
    elif putIV > 2*callIV:
        s = Stock(udlying)
        if get_volume(udlying) > 1000000 and s.price>10:
            High_IV_diff_list.append(udlying)
            print(udlying, "has put side skewed IV with req. met, ratio",putIV/callIV)
# %%

# if __name__ == '__main__':
print('running')
print('reading input')
option_list = csv_read (csv_name="optionable_list.csv")

#%%
#print("volume filtering")
#volume_filter_multi(high_iv_list)
#print(filtered_list)
#pd.options.mode.chained_assignment = None  # default='warn'

#%%
#Combine the two function above

start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(High_IV_diff_flag_ratio,option_list)
print(High_IV_diff_list)

# %%

    
    
    
