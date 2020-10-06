"""pedlarweb entry point."""

import datetime, requests, os 
import pandas as pd 
import numpy as np

# Setting up multiple apps
from dash import Dash
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Flask, render_template, redirect, url_for, request, jsonify
from werkzeug.serving import run_simple
from flask import render_template, redirect, url_for, request, jsonify

# Dash application
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output 
import dash_table
import plotly.graph_objs as go

# datafeed functions 
import quandl 
quandl.ApiConfig.api_key = os.environ.get('QUANDL')

# database
import pymongo 

# Technical analysis 
import pandas_ta as ta


## Custom trade models 


# Setting up flask server 
server = Flask(__name__,instance_relative_config=True)

# CSS
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', '/static/main.css']

# Setting up dash applications
dash_app1 = Dash(__name__, server = server, url_base_pathname='/quandl/', external_stylesheets=external_stylesheets )

# mongo functions 
def mongo2df(client,dbname,collectionname):
    
    db = client.get_database(dbname)
    df = pd.DataFrame(list(db[collectionname].find({})))
    try:
        df.drop(['_id'], axis=1,inplace=True)
        df.drop_duplicates(keep='last', inplace=True)
    except:
        print('Record not found',collectionname)
    client.close()
    return df 




# The mainpage for 
@server.route('/')
def main_page():
    return render_template('index.html')


# Plotly Applications

@server.route('/quandl')
def render_dashboard1():
    return redirect('/dash1')



QUANDL_OPTIONS = [
    {'label':'E-mini S&P 500 Futures','value':'CHRIS/CME_ES1'},
    {'label':'E-mini Dow Futures','value':'CHRIS/CME_YM1'},
    {'label':'E-mini NASDAQ 100 Futures','value':'CHRIS/CME_NQ1'},
    {'label':'S&P 500 Volatility Index VIX Futures','value':'CHRIS/CBOE_VX1'},
    {'label':'FTSE 100 Index Futures','value':'CHRIS/LIFFE_Z1'},
    {'label':'Cocoa Futures','value':'CHRIS/ICE_CC1'},
    {'label':'EURO STOXX 50 Index Futures','value':'CHRIS/EUREX_FESX1'},
    ]

# Dash samples 
dash_app1.layout = html.Div(children=[
    html.Span('Quandl Futures data'),
    dcc.Dropdown(
    id='quandl-symbols',
    options = QUANDL_OPTIONS ,
    value=['CHRIS/CME_ES1', 'CHRIS/CME_YM1'],
    multi=True
    ),

    dcc.Graph(
        id='qunadl-price-graph',
        figure=dict(
        data=[], 
        layout=dict(
            title='Historical price of Selected Futures',
            showlegend=True,
            legend=dict(
                x=0,
                y=1.0
            ),
            margin=dict(l=40, r=40, t=40, b=30)
        )
    ),
    style={'height': 500},
    ),
])


def _download_quandl_futures(symbol):
    price_df = quandl.get(symbol, start_date='1995-01-01', end_date=datetime.date.today())
    if symbol.split('/')[1].split('_')[0] in ['EUREX']:
        price_df = price_df[['Open','High','Low','Settle','Volume','Prev. Day Open Interest']]
        price_df.columns = ['Open','High','Low','Close','Volume','Open Interest']
        print('EUREX')
    if symbol.split('/')[1].split('_')[0] in ['CME']:
        price_df = price_df[['Open','High','Low','Last','Volume','Previous Day Open Interest']]
        price_df.columns = ['Open','High','Low','Close','Volume','Open Interest']
    if symbol.split('/')[1].split('_')[0] in ['CBOE']:
        price_df = price_df[['Open','High','Low','Close','Total Volume','Prev. Day Open Interest']]
        price_df.columns = ['Open','High','Low','Close','Volume','Open Interest']
    if symbol.split('/')[1].split('_')[0] in ['ICE']:
        price_df = price_df[['Open','High','Low','Settle','Volume','Prev. Day Open Interest']]
        price_df.columns = ['Open','High','Low','Close','Volume','Open Interest']
    if symbol.split('/')[1].split('_')[0] in ['LIFFE']:
        price_df = price_df[['Open','High','Low','Settle','Volume','Interest']]
        price_df.columns = ['Open','High','Low','Close','Volume','Open Interest']
    return price_df 



@dash_app1.callback(Output('qunadl-price-graph', 'figure'),
              [Input('quandl-symbols','value')])
def plot_quandl_data(quandlsymbols):
    try:
        trace = []
        for symbol in quandlsymbols:
            price_df =  _download_quandl_futures(symbol)
            print('{} data downloaded'.format(symbol))
            trace.append(go.Scatter(x=price_df.index, y=price_df['Close'], name=symbol, mode='lines',
                                marker={'size': 8, "opacity": 0.6, "line": {'width': 0.5}}, ))
        # layout of line graph 
        _layout=dict(
            title='Historical Price for selected futures',
            showlegend=True,
            legend=dict(
                x=0,
                y=1.0
            ),
            margin=dict(l=150, r=50, t=50, b=150)
        )
        return dict(data=trace, layout=_layout)
    except:
        return []

app = DispatcherMiddleware(server, {
    '/dash1': dash_app1.server,
})

if __name__ == "__main__":
    live = False
    if live:
        run_simple('127.0.0.1', 5000, app, use_reloader=False, use_debugger=True)
    else:
        run_simple('127.0.0.1', 5000, app, use_reloader=False, use_debugger=True)