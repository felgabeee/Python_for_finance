# import modules
import json
import requests
import pandas as pd
from tqdm.notebook import tqdm_notebook
import sqlite3
from datetime import datetime
import re
import matplotlib.pyplot as plt


def get_option_name_and_settlement(coin):
   
    # requests public API
    r = requests.get("https://test.deribit.com/api/v2/public/get_instruments?currency=" + coin + "&kind=option")
    result = json.loads(r.text)

    # get option name
    name = pd.json_normalize(result['result'])['instrument_name']
    name = list(name)

    # get option settlement period
    settlement_period = pd.json_normalize(result['result'])['settlement_period']
    settlement_period = list(settlement_period)

    return name, settlement_period


def get_option_data(coin):
    global coin_df

    # get option name and settlement
    coin_name = get_option_name_and_settlement(coin)[0]
    settlement_period = get_option_name_and_settlement(coin)[1]

    # initialize data frame
    coin_df = []

    # initialize progress bar
    pbar = tqdm_notebook(total=len(coin_name))

    # loop to download data for each Option Name
    for i in range(len(coin_name)):
        # download option data -- requests and convert json to pandas
        r = requests.get('https://test.deribit.com/api/v2/public/get_order_book?instrument_name=' + coin_name[i])
        result = json.loads(r.text)
        df = pd.json_normalize(result['result'])

        # add settlement period
        df['settlement_period'] = settlement_period[i]
        df["timestamp"] = df["timestamp"].map(lambda x : datetime.now())
        df=df.set_index(df["timestamp"])
        
        
        #Add specific column to differentiate call and puts
        df["C_or_P"] = df["instrument_name"].map(lambda x :x[-1])
               
        # append data to data frame
        coin_df.append(df)

        # update progress bar
        pbar.update(1)

    # finalize data frame
    coin_df = pd.concat(coin_df)
    df_calls = coin_df[coin_df["C_or_P"]=="C"]
    df_calls.sort_values(by=["instrument_name"],ascending=True)
    df_puts = coin_df[coin_df["C_or_P"]=="P"]
    df_puts.sort_values(by=["instrument_name"],ascending=True)
    coin_df = pd.concat([df_calls,df_puts])
    coin_df["strike"] = coin_df["instrument_name"].apply(lambda x : ''.join(re.findall('[0-9]+',str(re.findall('-[0-9]+-', x)))))
    
    #Rearange the columns order
    coin_df = coin_df[['instrument_name','underlying_price','strike',
    'mark_price', 'open_interest', 
    'mark_iv', 'last_price', 'interest_rate','greeks.vega',
    'greeks.theta', 'greeks.rho', 'greeks.gamma', 'greeks.delta']]
   
    # close the progress bar
    pbar.close() 
 
    return coin_df

#Get the live greek data

def get_greeks_data(greek,option_name):
    r = requests.get('https://test.deribit.com/api/v2/public/get_order_book?instrument_name=' + option_name)
    result = json.loads(r.text)
    result = result['result']["greeks"][f"{greek}"]
    return result
 
# Plot live option greeks movments
def plot_graph(greek,option_name,seconds):
    fig=plt.figure(figsize=(12,8))
    i=0
    x,y=[],[]
    while i < seconds:
        x.append(i)
        y.append(get_greeks_data(greek,option_name))
        plt.plot(x,y)
        plt.xlabel("Time in second")
        plt.ylabel(f"{greek} value")
        time.sleep(1)
        i+=1

