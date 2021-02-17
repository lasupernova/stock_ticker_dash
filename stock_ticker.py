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
import os
from dotenv import load_dotenv

# --- load api key ----
load_dotenv()
IEX_API_KEY = os.getenv('IEX_API_KEY')
ALPHA_API_KEY= os.getenv('ALPHA_API_KEY')


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
                        id='currency-selectos',
                        options=[
                            {'label': 'US Dollar', 'value': 'USD'},
                            {'label': 'Euro', 'value': 'EUR'},
                            {'label': 'Colombian Peso', 'value': 'COP'}
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
@app.callback(Output('stock_graph','figure'), [Input('stock_ticker','value')])
def update_plot(input_value):

    today = datetime.today()
    start_date = today - timedelta(weeks=12)
    end_date = today

    df = web.DataReader(input_value, 'iex', start_date, end_date, api_key=IEX_API_KEY)
    print(df)

    fig = {
            'data': [
                {'x': df.index, 'y': df.close}
                    ],
            'layout': dict(title=input_value) 
                    }
    return fig

# ----- run app -----
if __name__ == '__main__':
    app.run_server()
