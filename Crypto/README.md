# Crypto_data.py

This module does two main things:

First, it is using the Binance API to get historical data on any crypto for a given period of time.
In order to use this module you will need to create your own [Binance API](https://coinmatics.zendesk.com/hc/en-us/articles/360015574417-How-to-create-an-API-key-on-Binance).

Kind of data available:

- The price of a given crypto => price_token(pair)
- The Bid/Ask spread => bid_ask_wall(pair)
- Crypto historical data => get_historical_data(pair,start_date,log_returns=False)
- Index historical data => get_stocks_data(start,end)
- Crypto historical data for multiple cryptos => multiple_historical_data(Tickers,start_date)

The second part of the module is dedicated to create trading indicators:
 - RSI
 - Ichimoku
 - Exponential moving averages
 - Bolinger bands
 - Slope angle

# Crypto_options.py

This module creates a dataframe with real options data from the crypto exchange Deribit and produces the given dataframe outuput:


![alt text](https://github.com/felgabeee/Python_for_finance/blob/main/Images/df_crypto_options.PNG)

# Ichimoku_backtest.py

A simple backtest based only on the ichimoku indicator and more especially its Tenkan component.
The strategy consits of buying one unity of the asset if the price cross down the tenkan and if the spread (see formula inside the code) is lower than 2%.
Then, it tells you to sell one unity of the asset if the price cross up the tenkan and if the spread is lower than 2%.

The final output gives you bot PnL and the wining rate of the strategy.

You can also plot the different moments when you buy and sell the asset as the following:
![alt text](https://github.com/felgabeee/Python_for_finance/blob/main/Images/Ichimoku_backtest.PNG)
