import csv

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


def csv_read (csv_name="all_tickers.csv"):
    """
    read csv
    :param csv_name:
    :return: content list
    """
    content = list()
    with open(csv_name, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        content =[lines[0] for lines in csv_reader]

    return content

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
