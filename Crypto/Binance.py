from binance import Client
import pandas as pd
import time
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import tensorflow as tf
from tensorflow import keras

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os,sys
import pandas_datareader.data as web
import datetime
import seaborn as sns

%matplotlib notebook
secret_pharse = "1VtQljl8VUHE8xROySBJmVW4vTA0l1eJPG7aWkgIaRT5xGmP443bP7H1tD6q09ci"
API_key ="Ks7LSLAC0YVR5Nr5mNFlq5YuMPNWmvt4MCiGDg1R8YFHvDYv6fC2DbgyHqen4FTe"

client= Client(API_key,secret_pharse)



def price_token(pair):
    global df
    tickers = client.get_all_tickers()
    df_tickers =pd.DataFrame(tickers)
    df_tickers.set_index("symbol",inplace=True)

    df=df_tickers.loc[str(pair)].iloc[0]
    return float(df)

def bid_ask_wall(pair):
    global df_wall_ask, df_wall_bid
    bloc=client.get_order_book(symbol=pair)
    df_wall_ask =pd.DataFrame(bloc["asks"])
    df_wall_ask.columns =["Ask","Volume"]
    df_wall_bid =pd.DataFrame(bloc["bids"])
    df_wall_bid.columns =["Bid","Volume"]
    bid_ask_df =pd.concat([df_wall_bid,df_wall_ask], axis=1)
    bid_ask_df=bid_ask_df.astype(float)
    bid_ask_df["Spread"] = bid_ask_df["Ask"] - bid_ask_df["Bid"]
    bid_ask_df["Mid_point"] = (bid_ask_df["Ask"] + bid_ask_df["Bid"])/2
    bid_ask_df["Relative_Spread"] = bid_ask_df["Spread"] /  bid_ask_df["Mid_point"]
    return bid_ask_df

def get_stocks_data(start,end):
    global SP500,dow_jones,nasdaq
    SP500 = web.DataReader(['^GSPC'], 'yahoo', start, end)
    SP500 = SP500.fillna(SP500["Close"].rolling(window=3).mean())
    SP500 = SP500["Close"]
    SP500 = SP500.rename(columns={'^GSPC':"Close_S&P500"})
    SP500 = SP500.iloc[:,0]
    dow_jones = web.DataReader(['^DJI'], 'yahoo', start, end)
    dow_jones = dow_jones.fillna(dow_jones["Close"].rolling(window=3).mean())
    dow_jones = dow_jones["Close"]
    dow_jones = dow_jones.rename(columns={'^DJI':"Close dow_jones"})
    dow_jones = dow_jones.iloc[:,0]
    nasdaq = web.DataReader(['^IXIC'], 'yahoo', start, end)
    nasdaq = nasdaq.fillna(nasdaq["Close"].rolling(window=3).mean())
    nasdaq = nasdaq["Close"]
    nasdaq = nasdaq.rename(columns={'^IXIC':"Close_Nasdaq"})
    nasdaq=nasdaq.iloc[:,0]
    
    
def get_historical_data(pair,start_date,log_returns=False):
    global df_historical_data
    historical_data = client.get_historical_klines(str(pair),Client.KLINE_INTERVAL_1DAY,str(start_date))
    df_historical_data = pd.DataFrame(historical_data)
    df_historical_data.columns =  ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 
                    'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']
    df_historical_data['Open Time'] = pd.to_datetime(df_historical_data['Open Time']/1000, unit='s')
    df_historical_data['Close Time'] = pd.to_datetime(df_historical_data['Close Time']/1000, unit='s')
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote Asset Volume', 'TB Base Volume', 'TB Quote Volume']
    df_historical_data[numeric_columns]=df_historical_data[numeric_columns].apply(pd.to_numeric, axis=1)
    df_historical_data.set_index("Open Time", inplace =True)
    
    if log_returns == True:
        df_historical_data["Simple_returns"] = df_historical_data["Close"].pct_change()
        df_historical_data["log_returns"] = [np.log(rt +1) for rt in  df_historical_data["Simple_returns"]]
          
        
        
    
Tickers=["XTZUSDT","XRPUSDT","BNBUSDT","ETHUSDT","XMRUSDT","LTCUSDT","ADAUSDT","DOGEUSDT","DOTUSDT","AVAXUSDT","MATICUSDT","LINKUSDT","BTCUSDT","VETUSDT","KSMUSDT"] 

def multiple_historical_data(Tickers,start_date):
    global data
    df={}
    data = pd.DataFrame()
    for ticker in Tickers:
        df[f"{ticker}"]= get_historical_data(ticker,start_date)
        df[f"{ticker}"] =df_historical_data["Close"]
        data[f"{ticker}"]=df[f"{ticker}"]
    check_for_nan = data.isnull().sum()
    print("NaN values found:")
    print(check_for_nan)
    data = data.dropna(axis=0)
    data=data.sort_values(by="Open Time")
    
def denormalize(mean,std,data):
    return (data*std)+mean

def parse_na_values(df_column):
    for i in range(len(df_column)):
        if np.isnan(df_column[i]):
            df_column[i]=df_column[i-1]

                       