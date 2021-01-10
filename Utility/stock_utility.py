import csv
import requests
import time
import concurrent.futures
import requests
from urllib.parse import unquote, urlencode

from yahoo_fin import options

def find_optionable_stocks(udlying):
    """
    Check if the ticker is expired and add it to Global optional list
    :param udlying:  Input Ticket
    :return:  None
    """
    global optionable_list

    g = options.get_expiration_dates(udlying)
    if len(g):
        print(udlying)
        optionable_list.append(udlying)


def read_file(csv_name="all_tickers.csv"):
    """
    read csv
    :param csv_name:
    :return: content list
    """
    content = list()
    with open(csv_name, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        content = [lines[0] for lines in csv_reader]

    return content

def csv_write (list_in=list() ,csv_name="Filtered_list.csv"):
    """
    read csv
    :param csv_name:
    :return: content list
    """
    content = list()
    with open(csv_name, "w") as csv_file:
        write = csv.writer(csv_file)

    return content

def get_expiration(ticker="AAPL",time_diff=0):
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
    expirations = list()
    results = stock.get("optionChain", {}).get("result", [])
    if len(results) == 0:
        return expirations
    else:
        epoch_dates = results[0].get("expirationDates", None)
        expirations = [time.strftime('%Y-%m-%d', time.localtime(date + DAY)) for date in epoch_dates]
        return expirations


def get_volume(ticker="AAPL"):
    """
    Get stock's volume
    :param ticker: ticker name
    :return:
    """
    url = "https://www.alphaquery.com/data/stock-price-chart"
    params = {
        "ticker": ticker,
    }
    r = requests.get(url=url, params=params)
    stock_info = r.json()
    volume = stock_info["adjusted"][-1]["volume"]
    return volume


def get_stock(ticker="AAPL"):
    """
    Get stock info
    :param ticker: ticker name
    :return: stock info
    """
    url = f"https://query1.finance.yahoo.com/v7/finance/options/{ticker}"
    # params = {
    #     "ticker": ticker,
    # }
    r = requests.get(url=url)
    print(r)
    stock = r.json()
    return stock


def get_tickers():
    """
    Get available tickers
    :return: optionable_list, filtered_list
    """

    global filtered_list

    ## read all ticker names
    list_of_tickers = read_file(csv_name="all_tickers_V2.csv")
    print(list_of_tickers)
    print(len(list_of_tickers))

    ## find all available tickers
    start = time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(find_optionable_stocks, list_of_tickers)

    print(optionable_list)
    print(filtered_list)

    ## write back the results to text
    with open('optionable_list.txt', 'w') as f:
        for item in optionable_list:
            f.write("%s\n" % item)
    # print(len(optionable_list))
    # print(filtered_list)
    # print(len(filtered_list))
    print(f'Time taken: {time() - start}')

    return optionable_list, filtered_list


def get_volatility(ticker="AAPL", is_put=True):
    """
    Get stock's volatiliy
    :param ticker: ticker name
    :param is_put: put or get
    :return: list of json volatility data
    """
    url = "https://www.alphaquery.com/data/option-statistic-chart"
    params = {}
    if is_put:
        params = {
            "ticker": ticker,
            "perType": "30-Day",
            "identifier": "iv-put"
        }
    else:
        params = {
            "ticker": ticker,
            "perType": "30-Day",
            "identifier": "iv-call"
        }
    r = requests.get(url=url, params=params)
    iv = r.json()
    return iv


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
    # print(len(iv_lookahead))
    ivs = [k['value'] if k['value'] else 0.0 for k in iv_lookahead]

    iv_avg = sum(ivs) / lookahead
    return iv_avg, iv


# %%

def get_option_chain_barchart(ticker = "AAPL", expi ='2021-01-15', Type = "monthly"):
    get_url = r'https://www.barchart.com/etfs-funds/quotes/SPY/volatility-greeks'
    
    get_headers = {
    
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    }
    
    get_para = {
        #'expiration': '2021-01-15-m'
    }
    
    s = requests.Session()
    r = s.get(get_url, params=get_para, headers=get_headers)
    
    # %%
    api_url = r'https://www.barchart.com/proxies/core-api/v1/options/get'
    
    api_header = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'referer': f"{get_url}?{urlencode(get_para)}",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
        'X-XSRF-TOKEN': unquote(unquote(s.cookies.get_dict()['XSRF-TOKEN']))
    
    }
    api_para = {
        'fields': "symbol,baseSymbol,strikePrice,lastPrice,theoretical,volatility,delta,gamma,rho,theta,vega,volume,openInterest,volumeOpenInterestRatio,optionType,daysToExpiration,expirationDate,tradeTime,averageVolatility,symbolCode,symbolType",
        'baseSymbol': ticker,
        'groupBy': "optionType",
        'expirationDate': expi,
        'meta': 'field.shortName,expirations,field.description',
        'orderBy': 'strikePrice',
        'orderDir': 'asc',
        'expirationType': Type,
        'raw': '1'
    
    }
    
    r = s.get(api_url, params=api_para, headers=api_header)
    ##results
    j = r.json()
    return j





