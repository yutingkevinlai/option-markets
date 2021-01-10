
# %%
import requests
from urllib.parse import unquote, urlencode

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
        'fields': "symbol,baseSymbol,strikePrice,moneyness,bidPrice,midpoint,askPrice,lastPrice,priceChange,percentChange,volume,openInterest,volumeOpenInterestRatio,volatility,optionType,daysToExpiration,expirationDate,tradeTime,averageVolatility,symbolCode,symbolType",
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


option_info = get_option_chain_barchart(ticker = "AAPL", expi ='2021-01-15', Type = "monthly")
expirations_raw = option_info["data"]["Put"][0]
print(expirations_raw)
















