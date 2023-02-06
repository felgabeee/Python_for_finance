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
