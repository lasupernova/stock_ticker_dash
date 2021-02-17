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

# --- load api key ----
load_dotenv()
IEX_API_KEY = os.getenv('IEX_API_KEY')


# ----- dash object -----
app = dash.Dash()

app.layout = html.Div([
                html.H1('Comparative Stock Ticker'),
                html.H4('Start typing a stock ticker:'),
                html.Div([
                        dcc.Input(
                            id='stock_ticker',
                            value='TSLA'
                            )
                        ],
                        style=dict(width='70%', display='inline-block', padding=15)
                    ),
                html.Div([
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
                        style=dict(width='20%', display='inline-block', padding=15)
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
@app.callback(Output('stock_graph','figure'), [Input('stock_ticker','value'), Input('currency-selector', 'value')])
def update_plot(stock_ticker, selected_currency):

    today = datetime.today()
    start_date = today - timedelta(weeks=12)
    end_date = today

    df = web.DataReader(stock_ticker, 'iex', start_date, end_date, api_key=IEX_API_KEY)

    # calculate new df values if currency is changed
    if selected_currency!=None:
        exchange_matrix = exchange_rate_per_date(start_date, end_date, selected_currency) 

    
    print(selected_currency, '\n', exchange_matrix)

    fig = {
            'data': [
                {'x': df.index, 'y': df.close}
                    ],
            'layout': dict(title=stock_ticker) 
                    }
    return fig

# ----- functions -----

def exchange_rate_per_date(start_date, end_date, currency):

    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    url = f"https://api.exchangeratesapi.io/history?start_at={start_date}&end_at={end_date}&base=USD"
    
    response = requests.get(url)
    data = response.text
    parsed = json.loads(data)
    rates = parsed["rates"]
    
    exchange_rate_by_date = {date: rates[date][f'{currency}'] for date in rates.keys()}

    exchange_matrix = pd.Series(exchange_rate_by_date)
    exchange_matrix.index = pd.to_datetime(exchange_matrix.index)
    exchange_matrix.sort_index(inplace=True)
    
    return exchange_matrix

# ----- run app -----
if __name__ == '__main__':
    app.run_server()
