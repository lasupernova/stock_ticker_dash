#######
# Dashboard that allows the user to enter
# a stock ticker symbol into an input box, or to select
# symbols from a dropdown menu
######

# ---- imports ----
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime, timedelta
import pandas_datareader as web
import requests
import json
import os
from dotenv import load_dotenv
import pandas as pd

# --- load api key ----
load_dotenv()
IEX_API_KEY = os.getenv('IEX_API_KEY')


# ----- dash object -----
app = dash.Dash()

app.layout = html.Div([
                html.H1('Comparative Stock Ticker'),
                html.Div([
                        html.H4('Start typing a stock ticker:'),
                        dcc.Input(
                            id='stock_ticker',
                            value='TSLA',
                            style=dict(fontSize=20, width=75, verticalAlign='top')
                            )
                        ],
                        style=dict(width='30%', display='inline-block', padding=5)
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
                dcc.Graph(
                        id='stock_graph',
                        figure={
                            'data': [
                                {'x': [1,2], 'y': [3,1]}
                                    ],
                            'layout': dict(title='Pick a stock') 
                            }
                    )
])

# ----- callbacks -----
@app.callback(Output('stock_graph','figure'), 
            [Input('stock_ticker','value'), Input('currency-selector', 'value'),
             Input('date-picker','start_date'), Input('date-picker', 'end_date')])
def update_plot(stock_ticker, selected_currency, start_date, end_date):

    df = web.DataReader(stock_ticker, 'iex', start_date, end_date, api_key=IEX_API_KEY)
    df.sort_index(inplace=True)

    start_date = start_date.split(' ')[0]
    end_date = end_date.split(' ')[0]
    
    # calculate new df values if currency is changed
    if selected_currency!=None and selected_currency != 'USD':
        exchange_matrix = exchange_rate_per_date(start_date, end_date, selected_currency) 
        exchange_matrix.columns = ['exchange']
        df = pd.concat([df, exchange_matrix], axis=1)
        df['close'] = df['close'] * df['exchange']
        df.dropna(inplace=True)

    fig = {
        'data': [
            {'x': df.index, 'y': df.close}
                ],
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

# ----- run app -----
if __name__ == '__main__':
    app.run_server()
