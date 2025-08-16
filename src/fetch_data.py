import pandas as pd 
import ccxt 
import time

exchange = ccxt.binance()

symbol = 'BTC/USDT'
timeframe = '1d'
limit = 500 # number of data points
ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

df.to_csv('../data/btc_usdt.csv', index=False)
print("Saved to ../data/btc_usdt.csv")