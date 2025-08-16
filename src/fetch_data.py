import pandas as pd 
import ccxt 
import time

exchange = ccxt.binance()  # Connect to Binance

symbol = 'BTC/USDT'        # What to trade
timeframe = '1d'           # Daily candles
limit = 500                # Get 500 days of data
ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

# O = Open - Price when the period started
# H = High - Highest price during the period
# L = Low - Lowest price during the period
# C = Close - Price when the period ended
# V = Volume - How much was traded
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

df.to_csv('../data/btc_usdt.csv', index=False)
print("Saved to ../data/btc_usdt.csv")

# # Get market data
# ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1d', limit=500)

# # Get ticker info
# ticker = exchange.fetch_ticker('BTC/USDT')

# # Get order book
# orderbook = exchange.fetch_order_book('BTC/USDT')

# # Get recent trades
# trades = exchange.fetch_trades('BTC/USDT')