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