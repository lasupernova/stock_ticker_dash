#######
# Dashboard that allows the user to enter
# a stock ticker symbol into an input box, or to select
# symbols from a dropdown menu
######

# ---- imports ----
import dash
import dash_core_components as dcc
import dash_html_components as html

# ----- dash object -----
app = dash.Dash()

app.layout = html.Div([
                html.H1('Stock Ticker'),
                html.H4('Enter a stock ticker:'),
                dcc.Input(
                    id='stock_ticker'
                    value='TSLA' # initial default value
                ),
                dcc.Graph(
                    id='stock_graph'
                    figure={
                        'data': [
                            {'x': [1,2], 'y': [3,1]}
                        ]
                    }
                )
])

# ----- run app -----
if __name__ == '__main__':
    app.run_server()
