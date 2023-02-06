from Crypto.Crypto_options import *
#Get the data from a given period
get_historical_data("BTCUSDT","01-01-2021")
#Compute the daily returns
df_historical_data["Returns"] = df_historical_data["Close"].pct_change()
#Get ichimoku indicator defined in the Crypto_data.py module
ichimoku(df_historical_data)

def ichimoku_backtest(df):
    #Initialize variables
    open_position=False
    df.dropna(inplace=True)
    short=False
    long=False
    buy,sell =[],[]
    buy_prices,sell_prices=[],[]
    pnl=[]
    wining_rate=[]
    
    for i in range(1,len(df)):
        spread = abs(df.Close[i] - df.Tenkan[i-1])/df.Tenkan[i-1]
        
        #Catch a deep
        if df.Close.iloc[i-1]> df.Tenkan.iloc[i-1] and df.Close.iloc[i] < df.Tenkan.iloc[i] and spread <0.02:
            open_position=True
            long=True
            buy.append(i)
            buy_prices.append(df.Close[i])
            
            #We sell one candlestick after the pattern recognition
            sell.append(i+1)
            sell_prices.append(df.Close[i+1])
            result_of_the_trade = df.Close[i+1] - df.Close[i]
            pnl.append(result_of_the_trade)
            
            if result_of_the_trade < 0:
                wining_rate.append(0)
            else : wining_rate.append(1)
                
            open_position=False
            long=False
                
        #Short a pump
        if df.Close.iloc[i-1]< df.Tenkan.iloc[i-1] and df.Close.iloc[i] > df.Tenkan.iloc[i] and spread < 0.02:
            open_position=True
            short=True
            sell.append(i)
            sell_prices.append(df.Close[i])
            #We sell one candlestick after the pattern recognition
            buy.append(i+1)
            buy_prices.append(df.Close[i+1])
            result_of_the_trade = df.Close[i] - df.Close[i-1]
            pnl.append(result_of_the_trade)
            
            if result_of_the_trade < 0:
                wining_rate.append(0)
            else :
                wining_rate.append(1)
            open_position=False
            short=False
         
    plt.scatter(df.iloc[buy].index,df.iloc[buy].Close, marker="^",color="green")
    plt.scatter(df.iloc[sell].index,df.iloc[sell].Close, marker="^",color="red")
    plt.plot(df.Close, label="Prices")
    plt.plot(df.Tenkan, label="Tenkan",color="yellow")
    plt.show()
    try :
        wining_rate=sum(wining_rate)/len(wining_rate)
    except Exception as e:
        print(f"Pas de trades: {e}")
    return sum(pnl),wining_rate

if __name__ == '__main__':
    ichimoku_backtest(df_historical_data)      

#Print the dataframe
df_historical_data    