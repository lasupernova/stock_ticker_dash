import pandas as pd
from yahoo_fin import stock_info
import requests
from datetime import datetime, timedelta
import numpy as np

today = datetime.today().date()

def get_tickers():
    '''
    Get ticker symbols for stocks listed on major stock exchanges. 
    At time of writing, this function retrieves 9899 stock symbols
    '''

    print("Retrieving Stock Symbols...")

    dow_tickers = stock_info.tickers_dow()
    nasdaq_ticker = stock_info.tickers_nasdaq()
    sp500_ticker = stock_info.tickers_sp500()
    other_tickers = stock_info.tickers_other()

    all_tickers = list(set(dow_tickers+nasdaq_ticker+sp500_ticker+other_tickers))
    print(f"\nTotal number of stock symbols retrieved: {len(all_tickers)}")

    tickers_dict = {'DOW':dow_tickers, 'NASDAQ':nasdaq_ticker, 'SP500': sp500_ticker, 'others':other_tickers}
    for exchange_name, ticker_list in tickers_dict.items():
        print(f"\t{exchange_name}: {len(ticker_list)}")

    return all_tickers


def get_ticker_info():
    '''
    Get ticker information from IEX and save information in pandas DataFrame.
    Includes: ticker symbol, stock name, retieval date, type (currently only specified for "crypto").
    Uneccessary columns dropped: "isEnabled" and "iexId"
    '''
    r = requests.get('https://api.iextrading.com/1.0/ref-data/symbols')
    ticker_info = r.json()
    ticker_df = pd.json_normalize(ticker_info) #create pandas DataFrame form data in json-format
    ticker_df.drop(['isEnabled','iexId'], axis=1, inplace=True)

    return ticker_df


def check_alternate_spelling(all_tickers:list, ticker_df):
    '''
    Checks for alternate spelling and consolidates spelling of ticker symbol names in ticker symbol list retrieved by get_tickers() to spelling of stock information retrieved by get_ticker_info().
    Consolidation in order to identify which stock symbols in get_tickers()-output [list] are missing in get_ticker_info()-output [df].
    Takes a list and a pandas DataFrame as arguments. Returns a list of stock symbols that are present in list but missing from pandas DataFrame, after spelling consolidation.
    '''

    seemingly_missing = len([x for x in all_tickers if x not in ticker_df.symbol.values])

    # replace "$" or "-"" symbols with "-" or ".", if this alternate spelling is in concordance with data from IEX symbol names in ticker_df 
    all_tickers = [x.replace("$","-") if x.replace("$","-") in ticker_df.symbol.values else x for x in all_tickers]
    all_tickers = [x.replace("-",".") if x.replace("-",".") in ticker_df.symbol.values else x for x in all_tickers]

    missing = [x for x in all_tickers if x not in ticker_df.symbol.values]

    print(f"\nNumber of ticker symbols with alternate spelling, that were consolidated: {seemingly_missing - len(missing)}.") 

    return missing

def add_missing_tickers(tickers_to_add:list, ticker_df):
    '''
    Adds tickers from all_tickers missing from ticker_df to ticker_df.
    '''
    
    # create df from tickers_to_add in correct format, to add to ticker_df
    to_add = [{'symbol': symbol, 'name': np.nan, 'date': today.strftime("%Y-%m-%d"), 'type': np.nan}  for symbol in tickers_to_add]
    to_add_df = pd.json_normalize(to_add)
    
    # concatenate dfs
    combined_df = pd.concat([ticker_df, to_add_df], ignore_index=True)
    
    return combined_df



if __name__ == '__main__':
    ticker_list = get_tickers()
    stock_info_df = get_ticker_info()
    to_add = check_alternate_spelling(ticker_list, stock_info_df)
    add_missing_tickers(to_add, stock_info_df).to_csv("stock_info.csv")


