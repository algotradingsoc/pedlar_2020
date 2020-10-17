## Download data from Quandl, Alpaca 

import datetime, requests, os, json 
import pandas as pd 
import numpy as np 

## Quandl API 
import quandl 
quandl.ApiConfig.api_key = os.environ.get('QUANDL', None)

## Alapca API 
Alapca_API_key = os.environ.get('APCA_API_KEY_ID', None)
Alapca_API_secret_key = os.environ.get('APCA_API_SECRET_KEY', None)


## Build Arctic database 
from arctic import CHUNK_STORE, Arctic

a = Arctic('localhost')
a.initialize_library('Alpaca_Equity_daily', lib_type=CHUNK_STORE)
a.initialize_library('Alpaca_Equity_minute', lib_type=CHUNK_STORE)
a.initialize_library('Qunadl_Futures_daily', lib_type=CHUNK_STORE)

## Download Quandl price data

def download_quandl_futures(symbol, startdate='1950-01-01', enddate=datetime.date.today()):
    '''Returned Log price data from Quandl Futures with date as index.'''
    
    quandl.ApiConfig.api_key = os.environ.get('QUANDL', None)
    
    price_df = quandl.get(symbol, start_date=startdate, end_date=enddate)
    
    if 'Settle' in price_df.columns:
        price_df['Close'] = price_df['Settle']
    if 'Last' in price_df.columns:
        price_df['Close'] = price_df['Last']
    if 'Total Volume' in price_df.columns:
        price_df['Volume'] = price_df['Total Volume']
    if 'Prev. Day Open Interest' in price_df.columns:
        price_df['Open Interest'] = price_df['Prev. Day Open Interest']
    if 'Previous Day Open Interest' in price_df.columns:
        price_df['Open Interest'] = price_df['Previous Day Open Interest']
    if 'O.I.' in price_df.columns:
        price_df['Open Interest'] = price_df['O.I.']
    
    price_df = price_df[['Open','High','Low','Close','Volume','Open Interest']]
    price_df.columns = ['Open','High','Low','Close','Volume','Open Interest']
    logdf = np.log(price_df) - np.log(price_df).shift(1)
    logdf.index.name = 'Date'
    logdf['date'] = logdf.index
    return logdf.dropna()


def download_quandl_symbols():
    ''' 
    Download selected futures from Quandl which are updated recently (14 days) and with history longer than 20 years
    '''
    url = 'https://www.quandl.com/api/v3/databases/CHRIS/metadata?api_key={}'.format(quandl.ApiConfig.api_key)
    df = pd.read_csv(url,compression='zip')
    df['from_date'] = pd.to_datetime(df['from_date'])
    df['to_date'] = pd.to_datetime(df['to_date'])
    df['exchange'] = df['code'].str.split('_',expand=True)[0]
    selected_exchanges = ['CME','ICE', 'EUREX', 'LIFFE', 'SHFE', 'CBOE']
    df = df[ (df['to_date'] > datetime.datetime.now()-datetime.timedelta(days=14)) 
            & (df['from_date'] < datetime.datetime.now()-datetime.timedelta(days=7300))
            & df['exchange'].isin(selected_exchanges) ]
    df['code'] = 'CHRIS/' + df['code']
    return df.sort_values('from_date')


## Download Alpaca price data 

def download_alpaca_data(ticker, timeframe='1D', start='2007-12-31T21:30:00-04:00', end=datetime.datetime.now()):
    '''Returned Price data from Alpaca with date as index.'''
    headers = {
    'APCA-API-KEY-ID' : Alapca_API_key,
    'APCA-API-SECRET-KEY': Alapca_API_secret_key,
    }
    response = requests.get('https://data.alpaca.markets/v1/bars/{}?symbols={}&start={}&end={}'.format(timeframe,ticker,start,end),headers=headers)
    df = pd.DataFrame(json.loads(response.text)[ticker])
    if timeframe == '1D':
        df.index = [x.replace(hour=0,minute=0) for x in pd.to_datetime(df['t'],unit='s')]
        df.index.name = 'Date'
        df.columns = ['date','Open','High','Low','Close','Volume']
    else:
        df.index = [x for x in pd.to_datetime(df['t'],unit='s')]
        df.index.name = 'Datetime'
        df.columns = ['date','Open','High','Low','Close','Volume']
    df.drop('date',axis=1,inplace=True)
    logdf = np.log(df) - np.log(df).shift(1)
    logdf['date'] = logdf.index
    return logdf.dropna()



def download_alpaca_assets():
    url = 'https://paper-api.alpaca.markets/v2/assets'
    headers = {
    'APCA-API-KEY-ID' : Alapca_API_key,
    'APCA-API-SECRET-KEY': Alapca_API_secret_key,
    }
    response = requests.get(url,headers=headers)
    df = pd.DataFrame(response.json())
    valid = df[(df['shortable']) ]
    return valid



from joblib import Parallel, delayed

def _create_symbol(symbol,libname):
    try:
        a = Arctic('localhost')
        lib = a[libname]
        if libname == 'Alpaca_Equity_minute':
            df1 = download_alpaca_data(symbol, timeframe='minute',)
            lib.update(symbol, df1, chunk_range=df1.index, upsert=True)
        if libname == 'Alpaca_Equity_daily':
            df1 = download_alpaca_data(symbol, timeframe='1D',)
            lib.update(symbol, df1, chunk_range=df1.index, upsert=True)
        if libname == 'Quandl_Futures_daily':
            df1 = download_quandl_futures(symbol,)
            lib.update(symbol, df1, chunk_range=df1.index, upsert=True)
        return symbol
    except Exception as e: 
        print(e)
        

## Build database 
def build_database(libname='Alpaca_Equity_daily'):
    if libname in ['Alpaca_Equity_daily','Alpaca_Equity_minute','Alpaca_Equity_minute_new']:
        alpaca_syms = download_alpaca_assets()['symbol']
        params = [(i,libname) for i in alpaca_syms]
        with Parallel(n_jobs=10) as parallel:
            results = parallel(delayed(_create_symbol)(*i) for i in params)
        print('Alpaca symbols {}'.format(len(alpaca_syms)))
        print('Loaded {}'.format(len(results)))
    if libname in ['Quandl_Futures_daily']:
        quandl_syms = download_quandl_symbols()['code']
        params = [(i,libname) for i in quandl_syms]
        with Parallel(n_jobs=10) as parallel:
            results = parallel(delayed(_create_symbol)(*i) for i in params)
        print('Quandl symbols {}'.format(len(quandl_syms)))
        print('Loaded {}'.format(len(results)))


def _update_symbol(sym,libname,start):
    try:
        a = Arctic('localhost')
        lib = a[libname]
        if libname in ['Alpaca_Equity_minute','Alpaca_Equity_minute_new']:
            df1 = download_alpaca_data(sym, timeframe='minute', start=start)
            lib.update(sym, df1, chunk_range=df1.index, upsert=True)
        if libname == 'Alpaca_Equity_daily':
            df1 = download_alpaca_data(sym, timeframe='1D', start=start)
            lib.update(sym, df1, chunk_range=df1.index, upsert=True)
        if libname in ['Quandl_Futures_daily']:
            df1 = download_quandl_futures(sym, startdate=start)
            lib.update(sym, df1, chunk_range=df1.index, upsert=True)
        return sym
    except Exception as e: 
        print(e)

## Update database
def update_database(arcticonn, libname='Alpaca_Equity_daily' , lookback=10):
    lib = arcticonn[libname]
    if libname in ['Alpaca_Equity_daily','Alpaca_Equity_minute','Alpaca_Equity_minute_new']:
        start = datetime.datetime.now() - datetime.timedelta(days=lookback)
        start = start.replace(microsecond=0).isoformat() + '-04:00'
        n_jobs = 10
        symbols = download_alpaca_assets()['symbol']
    if libname in ['Quandl_Futures_daily']:
        start = datetime.datetime.now() - datetime.timedelta(days=lookback)
        n_jobs = 10
        symbols =  download_quandl_symbols()['code']
    params = [(i,libname,start) for i in symbols]
    with Parallel(n_jobs=n_jobs) as parallel:
        results = parallel(delayed(_update_symbol)(*i) for i in params)
    print('Library symbols {}'.format(len(symbols)))
    print('Updated {}'.format(len(results)))

if __name__ == "__main__":
    import sys
    method = sys.argv[1]
    try:
        library = sys.argv[2]
    except IndexError:
        library = 'Alpaca_Equity_daily'
    try:
        lookback = int(sys.argv[3])
    except IndexError:
        lookback = 20     

    if method == 'build':
        a = Arctic('localhost')
        a.initialize_library('Alpaca_Equity_daily', lib_type=CHUNK_STORE)
        a.initialize_library('Alpaca_Equity_minute', lib_type=CHUNK_STORE)
        a.initialize_library('Alpaca_Equity_minute_new', lib_type=CHUNK_STORE)
        a.initialize_library('Quandl_Futures_daily', lib_type=CHUNK_STORE)
        build_database(library)
        
    if method == 'update':
        a = Arctic('localhost')
        a.initialize_library('Alpaca_Equity_daily', lib_type=CHUNK_STORE)
        a.initialize_library('Alpaca_Equity_minute', lib_type=CHUNK_STORE)
        a.initialize_library('Alpaca_Equity_minute_new', lib_type=CHUNK_STORE)
        a.initialize_library('Quandl_Futures_daily', lib_type=CHUNK_STORE)
        update_database(a,library, lookback)