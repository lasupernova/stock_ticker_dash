#######
# Dashboard that allows the user to enter
# a stock ticker symbol into an input box, or to select
# symbols from a dropdown menu
######

# ---- imports ----
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from datetime import datetime, timedelta
import requests
import json
import os
import pandas as pd
import yfinance as yf
import numpy as np
from ticker_options import ticker_options
from yahoo_fin import stock_info

ticker_options = ticker_options()

# ----- dash object -----
app = dash.Dash()

app.layout = html.Div([
                html.H1('Compare your stock gains'),
                html.Div([
                        html.H4('Start typing a stock ticker:'),
                        dcc.Dropdown(
                            id='stock_ticker',
                            options=ticker_options,
                            multi=True,
                            value=['TSLA']
                            )
                        ],
                        style=dict(width='90%', display='inline-block', verticalAlign='top', padding=5)
                    ),
                html.Div([
                        html.H4('Select a currency'),
                        dcc.Dropdown(
                            id='currency-selector',
                            options=[
                                {'label': 'US Dollar', 'value': 'USD'},
                                {'label': 'Euro', 'value': 'EUR'},
                                {'label': 'Canadian Dollar', 'value': 'CAD'}
                            ],
                            placeholder='Change Currency'
                                )
                            ],
                        style=dict(width='10%', display='inline-block', paddingLeft=5, horizontalAlign='left', verticalAlign='top')
                    ),
                html.Div([
                        html.H4('Change the dates'),
                        dcc.DatePickerRange(
                            id='date-picker',
                            min_date_allowed=datetime(2010,1,1),
                            max_date_allowed=datetime.today(),
                            start_date=datetime.today() - timedelta(weeks=4),
                            end_date=datetime.today(),
                            day_size=25
                                )
                            ],
                        style=dict(fontSize=15, width='30%', display='inline-block', paddingLeft=5, horizontalAlign='left', verticalAlign='top')
                    ),
                html.Div([
                        html.H4(''),
                        html.Button(id='submit_button',
                                n_clicks=0,
                                children="Submit",
                                style=dict(fontSize=22, marginLeft='30px', paddingLeft=5, horizontalAlign='left', verticalAlign='bottom')
                            )
                    ], style=dict(display='inline-block')),
                dcc.Graph(
                        id='stock_graph',
                        figure={
                            'data': [
                                {'x': [1,2], 'y': [3,1]}
                                    ],
                            'layout': dict(title='Pick a stock') 
                            },
                        style = dict(width='65%', display='inline-block')
                    ),
                html.Div([
                        html.H4("Today's most interesting stock")
                    ],
                    style = dict(width='25%', display='inline-block'))
])

# ----- callbacks -----
@app.callback(Output('stock_graph','figure'), 
            [Input('submit_button', 'n_clicks')],
            [State('stock_ticker','value'), State('currency-selector', 'value'),
             State('date-picker','start_date'), State('date-picker', 'end_date')])
def update_plot(n_clicks, stock_ticker, selected_currency, start_date, end_date):

    # extract date-portion of date-time string and create datetime-object for passing to yf.Ticker-object
    if type(start_date) == type(end_date) == str:

        # split date into date and time parts - reason: callback supplies date incl. time on startup, but only date-section upon selection in date_pickedr 
        s_date = start_date.split()[0]
        e_date = end_date.split()[0]

        # yfinance requires datetime-objects for start and end-arguments, but the callback-Input() passes string values
        try:
            start_date_yf = datetime.strptime(s_date, '%Y-%m-%d').date()
            end_date_yf = datetime.strptime(e_date, '%Y-%m-%d').date()
        except Exception as e:
            print('Exception captures: ', e)

    traces = []

    for chosen_stock in stock_ticker:
        ticker = yf.Ticker(chosen_stock)
        df = ticker.history(start=start_date_yf,  end=end_date_yf)
        df.sort_index(inplace=True)
        traces.append({'x': df.index, 'y': df['Close'], 'name': chosen_stock})


    
    # calculate new df values if currency is changed
    if selected_currency!=None and selected_currency != 'USD':
        # counter = workaround
        counter=0 #TODO: check why code breaks on second iteration (when m>one stock selected) when using idx = traces.index(stock)
        for stock in traces:
            # get stock prices for current iteration
            df = stock['y'].to_frame()
            # get exchange rate
            exchange_matrix = exchange_rate_per_date(s_date, e_date, selected_currency) 
            exchange_matrix = df_index_to_datetime(exchange_matrix) #convert exchange_matrix index to datetime, becsaue df index is also datetime and need to be the same for pd.concat()
            exchange_matrix.columns = ['exchange']
            # calculate prixe in chosen currency
            df = pd.concat([df, exchange_matrix], axis=1)
            df['Close'] = df['Close'] * df['exchange']
            df.dropna(inplace=True)
            # save new values to traces
            traces[counter]['y'] = df['Close'] 
            counter+=1


    fig = {
        'data': traces,
        'layout': dict(title=stock_ticker) 
                }

    return fig

# ----- functions -----

def exchange_rate_per_date(start_date, end_date, currency):

    url = f"https://api.exchangeratesapi.io/history?start_at={start_date}&end_at={end_date}&base=USD"
    
    response = requests.get(url)
    data = response.text
    parsed = json.loads(data)
    # print(parsed.keys()) #uncomment for troubleshooting
    rates = parsed["rates"]
    
    exchange_rate_by_date = {date: rates[date][f'{currency}'] for date in rates.keys()}

    exchange_matrix = pd.Series(exchange_rate_by_date).to_frame()
    exchange_matrix.sort_index(inplace=True)
    
    return exchange_matrix

def df_index_to_datetime(input_df):
    input_df.index = pd.to_datetime(input_df.index)
    return input_df

# ----- run app -----
if __name__ == '__main__':
    app.run_server(debug=True)

def stock_ratings(ticker):
    df = ticker.recommendations
    print(df)

def day_gainers():
    gainers = stock_info.get_day_gainers(10)
    return gainers
