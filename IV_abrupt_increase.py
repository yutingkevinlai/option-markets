# %%

import concurrent.futures
from wallstreet import Stock, Call, Put

from Utility.stock_utility import *

optionable_list = []
filtered_list = []
high_iv_list = []


# %%
abrupt_increase_list = list()

def detect_volatility_increase(ticker="AAPL"):
    """
    Calculate avg volatiliy
    :param ticker:  ticker name
    :param lookahead: lookahead
    :return:
    """
    print(ticker)
    s = Stock(ticker)
    global abrupt_increase_list
    if get_volume(ticker) > 5000000 and s.price > 10:
        ivput_json = get_volatility(ticker, is_put=True)
        ivcall_json = get_volatility(ticker, is_put=False)
        ivput_now, ivput_past = ivput_json[-1]["value"], ivput_json[-2]["value"]
        ivcall_now, ivcall_past = ivcall_json[-1]["value"], ivcall_json[-2]["value"]
        # get the most recent values
        if ivput_now > 1.3 * ivput_past and ivput_now > 0.3:
            # s = Stock(ticker)
            # if get_volume(ticker) > 1000000 and s.price>10:
            print(ticker, "has abrupt increase in volatility")
            abrupt_increase_list.append(ticker)
        elif ivcall_now > 1.3 * ivcall_past and ivcall_now > 0.3:
            # s = Stock(ticker)
            # if get_volume(ticker) > 1000000 and s.price>10:
            print(ticker, "has abrupt increase in volatility")
            abrupt_increase_list.append(ticker)

# %%

# if __name__ == '__main__':
print('running')
print('reading input')
option_list = read_file(csv_name="optionable_list.csv")

#%%
#print("volume filtering")
#volume_filter_multi(high_iv_list)
#print(filtered_list)
#pd.options.mode.chained_assignment = None  # default='warn'

#%%
#Combine the two function above

start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(detect_volatility_increase,option_list)
print(abrupt_increase_list)
# abrupt_increase_list = list()
# %%
