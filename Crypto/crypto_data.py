from binance import Client
import pandas as pd
import time
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import tensorflow as tf
from tensorflow import keras
from scipy.stats import linregress
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os,sys
import pandas_datareader.data as web
import datetime
import seaborn as sns

%matplotlib notebook
secret_pharse = "" # Put your secret phrase here
API_key ="" # Put your API here

client= Client(API_key,secret_pharse)

###################### Trading Indicators ###############################

def ichimoku(data):
    nine_period_high = data['High'].rolling(window= 9).max()
    nine_period_low = data['Low'].rolling(window= 9).min()
    period26_high= data['High'].rolling(window= 26).max()
    period26_low=data['Low'].rolling(window= 26).max()
    period52_high= data['High'].rolling(window= 52).max()
    period52_low=data['Low'].rolling(window= 52).max()
    data["Tenkan"]= (nine_period_high + nine_period_low)/2
    data["Kijun"]= (period26_high+period26_low)/2
    data["Chikou"]=data["Close"].shift(-26)
    data["Senkou_Span_A"] = ((data["Tenkan"] + data["Kijun"] )/2).shift(26)
    data["Senkou_Span_B"] = ((period52_low + period52_high )/2).shift(26)
    return data

def RSI(data,nb_period):
    data["Spread"] = data["Close"].diff()
    ret = data["Spread"]
    up = []
    down = []
    for i in range(len(ret)):
        if ret[i] < 0:
            up.append(0)
            down.append(ret[i])
        else:
            up.append(ret[i])
            down.append(0)
    up_series = pd.Series(up)
    down_series = pd.Series(down).abs()
    up_ewm = up_series.ewm(com = nb_period - 1, adjust = False).mean()
    down_ewm = down_series.ewm(com = nb_period - 1, adjust = False).mean()
    rs = up_ewm/down_ewm
    rsi = 100 - (100 / (1 + rs))
    rsi = list(rsi)
    data["RSI"] = rsi

def ewm(data,nb_period):
    data[f"ewm_{nb_period}"]=data["Close"].rolling(window=nb_period).mean()

def bolinger(data,nb_period,nb_std):
    ewm(data,nb_period)
    sigma = data["Close"].rolling(nb_period, min_periods=nb_period).std()
    data["U_bound"]= data[f"ewm_{nb_period}"] + (nb_std*sigma)
    data["L_bound"]= data[f"ewm_{nb_period}"] - (nb_std*sigma)
    
def slope_angle(data,timeframe = 7):
    data["Midprice"] = (data["High"] + data["Low"]) / 2
    data[f"{timeframe}_days_candlestick_midpoint"] = data.Midprice.rolling(window = timeframe).mean()
    data["slope"] = np.degrees(np.arctan(data[f"{timeframe}_days_candlestick_midpoint"]))

###################### Functions to get the data ###############################
    
def price_token(pair):
    global df
    tickers = client.get_all_tickers()
    df_tickers = pd.DataFrame(tickers)
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
    df_historical_data = df_historical_data[['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Number of Trades']]
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Number of Trades']
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
                       
