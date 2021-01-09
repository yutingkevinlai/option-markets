# %%
import concurrent.futures

from wallstreet import Stock, Call, Put

from Utility.stock_utility import *
from option_selecting import find_score_each_expiration

optionable_list = []
filtered_list = []
high_iv_list = []

#%%

High_IV_diff_list=list()
def High_IV_diff_flag(udlying):
    callIV = get_volatility(udlying, is_put=False)[-1]['value']
    putIV = get_volatility(udlying, is_put=True)[-1]['value']

    if abs(callIV - putIV) > 0.5:
        print(udlying, "has large IV diff")
        s = Stock(udlying)
        if get_volume(udlying) > 1000000 and s.price > 10:
            High_IV_diff_list.append(udlying)
            if callIV > putIV:
                print(udlying, "has call side skewed IV with req. met, diff", abs(callIV - putIV))
            elif putIV > callIV:
                print(udlying, "has put side skewed IV with req. met, diff", abs(callIV - putIV))


def High_IV_diff_flag_ratio(udlying):

    callIV = get_volatility(udlying, is_put=False)[-1]['value']
    putIV = get_volatility(udlying, is_put=True)[-1]['value']
    if callIV > 2 * putIV:
        s = Stock(udlying)
        if get_volume(udlying) > 1000000 and s.price > 10:
            High_IV_diff_list.append(udlying)
            print(udlying, "has call side skewed IV with req. met, ratio", callIV / putIV)
    elif putIV > 2 * callIV:
        s = Stock(udlying)
        if get_volume(udlying) > 1000000 and s.price > 10:
            High_IV_diff_list.append(udlying)
            print(udlying, "has put side skewed IV with req. met, ratio", putIV / callIV)


# %%

# if __name__ == '__main__':
print('running')
print('reading input')
option_list = read_file(csv_name="optionable_list.csv")
print("reading done")

# %%
# print("volume filtering")
# volume_filter_multi(high_iv_list)
# print(filtered_list)
# pd.options.mode.chained_assignment = None  # default='warn'


# %%
# Combine the two function above

print("Processing")
start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    executor.map(High_IV_diff_flag_ratio, option_list)
print(High_IV_diff_list)
print("Processing Done")
