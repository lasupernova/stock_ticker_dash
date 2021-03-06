'''
Creates list of dicts containing label and value information to pass on to dcc.Dropdown for options parameter.
'''
# ----- imports -----
import pandas as pd


def ticker_options():
    # ----- import stock and ticker information -----

    ticker_info = pd.read_csv("stock_info.csv")
    # ticker_info = ticker_info.iloc[:20]

    # ----- create options list to pass to dash dropdown menu -----

    ticker_options = []
    # iterate over ticker symbols, create list of dict with label to be visible to user (in dcc.Dropdown) and value
    for stock in ticker_info.index:
        data_dict = {}
        cond2 = (str(ticker_info.iloc[stock]['name']) != 'nan')
        cond1 = (str(ticker_info.iloc[stock]['name']) != 'nan' and str(ticker_info.iloc[stock]['type']) != 'crypto')
        name = str(ticker_info.iloc[stock]['name']) if cond1 else str(ticker_info.iloc[stock]['name'])+" [CRYPTO]" if cond2  else str(ticker_info.iloc[stock]['symbol']) 

        if name == 'nan':
            continue
        else:
            data_dict['label'] = str(name)
            symbol = ticker_info.iloc[stock]['symbol']
            data_dict['value'] = symbol
            ticker_options.append(data_dict)
    
    return ticker_options


# ----- run app -----
if __name__ == '__main__':
    print(len(ticker_options()))