"""pedlarweb entry point."""

import datetime 
import pandas as pd 
import requests 

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

# database
# TO-DO push password to env var 
import pymongo 



# Setting up flask server 
server = Flask(__name__,instance_relative_config=True)
# Load configuration
server.config.from_pyfile('config.py')

# CSS
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', '/static/main.css']

# Setting up dash applications
dash_app1 = Dash(__name__, server = server, url_base_pathname='/leaderboard/', external_stylesheets=external_stylesheets )
# dash_app2 = Dash(__name__, server = server, url_base_pathname='/orderbook/', external_stylesheets=external_stylesheets )
dash_app3 = Dash(__name__, server = server, url_base_pathname='/iex/', external_stylesheets=external_stylesheets )
dash_app4 = Dash(__name__, server = server, url_base_pathname='/pnl/', external_stylesheets=external_stylesheets )

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


# create new backtest record 

@server.route("/user", methods=['POST'])
def user_record():
    password = os.environ.get('algosocdbpw', 'algosocadmin')
    client = pymongo.MongoClient("mongodb+srv://algosocadmin:{}@icalgosoc-9xvha.mongodb.net/test?retryWrites=true&w=majority".format(password))
    db = client['Pedlar_dev']
    req_data = request.get_json()
    user = req_data.get('user', 'sample')
    agent = req_data.get('agent', 'sample')
    # compute tradesession id 
    tradesessionid = db['Counter'].find_one({})['counter'] + 1 
    db['Counter'].update_one({},{"$set":{'counter':tradesessionid}})
    return jsonify(username=user, tradesession=tradesessionid)

# update leaderboard after backtest 
@server.route("/tradesession", methods=['POST'])
def tradesession():
    password = os.environ.get('algosocdbpw', 'algosocadmin')
    client = pymongo.MongoClient("mongodb+srv://algosocadmin:{}@icalgosoc-9xvha.mongodb.net/test?retryWrites=true&w=majority".format(password))
    db = client['Pedlar_dev']
    req_data = request.get_json()
    user = req_data.get('user_id', 0)
    agent = req_data.get('agent', 'sample')
    tradesessionid = req_data.get('tradesession', 0)
    pnl = req_data.get('pnl', -10000)
    sharpe = req_data.get('sharpe', -100)
    # Add to leaderboard table 
    leaderboard = db['Leaderboard']
    leaderboard.update_one( {'backtest_id':tradesessionid} , {"$set":{'user_id':user, 'agent':agent, 'backtest_id':tradesessionid, 'pnl':pnl, 'sharpe':sharpe}}, upsert=True)
    return jsonify(username=user, tradesession=tradesessionid)

@server.route("/portfolio/<backtestid>", methods=['POST'])
def portfolio(backtestid):
    password = os.environ.get('algosocdbpw', 'algosocadmin')
    client = pymongo.MongoClient("mongodb+srv://algosocadmin:{}@icalgosoc-9xvha.mongodb.net/test?retryWrites=true&w=majority".format(password))
    db = client['Pedlar_dev']
    req_data = request.get_json()
    tradesessionid = str(req_data.get('tradesession', 0))
    # create capped collection 
    if not str(tradesessionid) in db.list_collection_names():
        db.create_collection(str(tradesessionid), capped=True, size=5000000, max=100)
    portfolio = db[tradesessionid]
    portfolio.insert_one(req_data)
    return jsonify(tradesession=tradesessionid)




# Plotly Applications

@server.route('/leaderboard')
def render_dashboard():
    return redirect('/dash1')


@server.route('/sample')
def render_dashboard3():
    return redirect('/dash3')

@server.route('/pnl')
def render_dashboard4():
    return redirect('/dash4')

# Dash samples 



dash_app1.layout = html.Div(children=[
    html.Div(id='leaderboard-header'),
    dash_table.DataTable(
    id='leaderboard',
    columns=[],
    style_table={
        'height': '300px',
        'overflowY': 'scroll',
        'border': 'thin lightgrey solid'
    },
    ),
    dcc.Interval(
        id='interval-leaderboard',
        interval=1000*60, # in milliseconds
        n_intervals=0
    )
])

@dash_app1.callback(Output('leaderboard-header', 'children'),
              [Input('interval-leaderboard', 'n_intervals')])
def update_leaderboard_header(n):
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    return [
        html.Span('Current Datetime: {}'.format(now))
    ]


@dash_app1.callback(Output('leaderboard', 'columns'),
              [Input('interval-leaderboard', 'n_intervals')])
def update_leaderboard(n):
    password = os.environ.get('algosocdbpw', 'algosocadmin')
    client = pymongo.MongoClient("mongodb+srv://algosocadmin:{}@icalgosoc-9xvha.mongodb.net/test?retryWrites=true&w=majority".format(password))
    data = mongo2df(client,'Pedlar_dev','Leaderboard')
    names = data.columns 
    return [{"name": i, "id": i} for i in names]
  

@dash_app1.callback(Output('leaderboard', 'data'),
              [Input('interval-leaderboard', 'n_intervals')])
def update_leaderboard_data(n):
    try:
        password = os.environ.get('algosocdbpw', 'algosocadmin')
        client = pymongo.MongoClient("mongodb+srv://algosocadmin:{}@icalgosoc-9xvha.mongodb.net/test?retryWrites=true&w=majority".format(password))
        data = mongo2df(client,'Pedlar_dev','Leaderboard')
        return data.to_dict('records')
    except:
        return []



iex_table_cols = ['time', 'exchange', 'ticker', 'bid', 'ask', 'bidsize', 'asksize']
iex_columns = [{"name": i, "id": i} for i in iex_table_cols]

dash_app3.layout = html.Div(children=[
    html.Span('IEX Orderbook'),
    dcc.Dropdown(
    id='iex-symbols',
    options=[],
    value=['SPY', 'QQQ'],
    multi=True
    ),
    dash_table.DataTable(
    id='iex',
    columns=iex_columns,
    data=[],
    style_table={
        'height': '300px',
        'overflowY': 'scroll',
        'border': 'thin lightgrey solid'
    },
    ),
    dcc.Interval(
        id='interval-iex',
        interval=2*1000, # in milliseconds
        n_intervals=0
    ),
    dcc.Interval(
        id='interval-symbol',
        interval=60*60*1000, # in milliseconds
        n_intervals=0
    ),
])


@dash_app3.callback(Output('iex-symbols', 'options'),
              [Input('interval-symbol', 'n_intervals')])
def update_iex_symbol(n):
    try:
        iexbaseurl = 'https://api.iextrading.com/1.0'
        iextopsurl = iexbaseurl + '/ref-data/symbols'
        r = requests.get(iextopsurl)
        data = pd.DataFrame(r.json())
        df = pd.DataFrame()
        df['label'] = data['name']
        df['value'] = data['symbol']
        return df.to_dict('records')
    except:
        return [{'label':'SPDR S&P 500 ETF TRUST','value':'SPY'}]

@dash_app3.callback(Output('iex', 'data'),
              [Input('interval-iex', 'n_intervals'),Input('iex-symbols','value')])
def update_iex_data(n,tickers):
    try:
        query_string = ','.join(tickers)
        df = pedlaragent.iex.get_TOPS(query_string) 
        return df.to_dict('records')
    except:
        return []

dash_app4.layout = html.Div(children=[
    html.Span('Portfolio Value'),
    dcc.Dropdown(
    id='backtest-ids',
    options=[],
    value=[],
    multi=False
    ),
    dcc.Graph(
        id='pnl-graph',
        figure=dict(
        data=[], 
        layout=dict(
            title='Portfolio value of most recent 10 trades',
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
    dcc.Interval(
        id='interval-backtest',
        interval=2*1000, # in milliseconds
        n_intervals=0
    ),
])

@dash_app4.callback(Output('backtest-ids', 'options'),
              [Input('interval-backtest', 'n_intervals')])
def update_backtest_ids(n):
    try:
        password = os.environ.get('algosocdbpw', 'algosocadmin')
        client = pymongo.MongoClient("mongodb+srv://algosocadmin:{}@icalgosoc-9xvha.mongodb.net/test?retryWrites=true&w=majority".format(password))
        db = client['Pedlar_dev']
        system_collections = ['Counter','Leaderboard']
        all_collections = db.list_collection_names()
        backtest_collections = list(set(all_collections)-set(system_collections))
        df = pd.DataFrame()
        df['label'] = backtest_collections
        df['value'] = backtest_collections
        return df.to_dict('records')
    except:
        return [{'label':'1','value':'1'}]


@dash_app4.callback(Output('pnl-graph', 'figure'),
              [Input('interval-backtest', 'n_intervals'),Input('backtest-ids', 'value')])
def update_backtest_data(n,backtestid):
    try:
        password = os.environ.get('algosocdbpw', 'algosocadmin')
        client = pymongo.MongoClient("mongodb+srv://algosocadmin:{}@icalgosoc-9xvha.mongodb.net/test?retryWrites=true&w=majority".format(password))
        selected = ['porftoliovalue']
        dff = mongo2df(client,'Pedlar_dev',backtestid)
        trace = []
        for type in selected:
            trace.append(go.Scatter(x=dff['time'], y=dff[type], name=backtestid, mode='lines',
                                marker={'size': 8, "opacity": 0.6, "line": {'width': 0.5}}, ))
        # layout of line graph 
        _layout=dict(
            title='Portfolio value',
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

# Linking diffrent application

app = DispatcherMiddleware(server, {
    '/dash1': dash_app1.server,
    '/dash3': dash_app3.server,
    '/dash4': dash_app4.server,
})

if __name__ == "__main__":
    live = False
    if live:
        run_simple('127.0.0.1', 5000, app, use_reloader=False, use_debugger=True)
    else:
        run_simple('127.0.0.1', 5000, app, use_reloader=False, use_debugger=True)