# %%
import requests
from urllib.parse import unquote

# %%


geturl = r'https://www.barchart.com/etfs-funds/quotes/SPY/volatility-greeks'
apiurl = r'https://www.barchart.com/proxies/core-api/v1/options/get'

getheaders = {

    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
}

getpay = {
    'expiration': '2021-01-15-m'
}

s = requests.Session()
r = s.get(geturl, params=getpay, headers=getheaders)

# %%
headers = {
    'accept': 'application/json',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': "https://www.barchart.com/etfs-funds/quotes/SPY/volatility-greeks?expiration=2021-01-15-m",
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
    'X-XSRF-TOKEN': unquote(unquote(s.cookies.get_dict()['XSRF-TOKEN']))

}
payload = {
    'fields': "symbol,baseSymbol,strikePrice,lastPrice,theoretical,volatility,delta,gamma,rho,theta,vega,volume,openInterest,volumeOpenInterestRatio,optionType,daysToExpiration,expirationDate,tradeTime,averageVolatility,symbolCode,symbolType",
    'baseSymbol': 'SPY',
    'groupBy': "optionType",
    'expirationDate': '2021-01-15',
    'meta': 'field.shortName,expirations,field.description',
    'orderBy': 'strikePrice',
    'orderDir': 'asc',
    'expirationType': 'monthly',
    'raw': '1'

}

r = s.get(apiurl, params=payload, headers=headers)
j = r.json()
print(j)
