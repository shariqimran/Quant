"""
RSI (Relative Strength Index) Trading Strategy

RSI is a momentum oscillator that measures the speed and magnitude of price changes.
It compares recent gains to recent losses over a specified period (typically 14 days)
and scales the result from 0 to 100.

What RSI tells us:
- RSI > 70: Asset is overbought (potentially overvalued, likely to reverse downward)
- RSI < 30: Asset is oversold (potentially undervalued, likely to reverse upward)  
- RSI = 50: Neutral momentum
- Divergence: When price makes new highs/lows but RSI doesn't follow, signals trend reversal

Trading Applications:
- Mean reversion: Buy oversold, sell overbought
- Trend confirmation: RSI staying above 50 in uptrends, below 50 in downtrends
- Divergence signals: Price/RSI divergence often precedes reversals
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('../data/btc_usdt.csv', parse_dates=['timestamp'])

def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)) # RSI formula:
    return rsi

df['RSI'] = calculate_rsi(df)

# 50-day MA filter
df['MA_50'] = df['close'].rolling(window=50).mean()

initial_cash = 10000
cash = initial_cash
btc = 0
in_position = False
trade_log = []

# Strategy Logic
for i in range(1, len(df)):
    row = df.iloc[i]
    if pd.isna(row['RSI']) or pd.isna(row['MA_50']):
        continue

    # Buy Condition
    if not in_position and row['RSI'] < 40 and row['close'] > row['MA_50']:
    # if not in_position and row['RSI'] < 40:
        btc = cash / row['close']
        cash = 0
        in_position = True
        trade_log.append((row['timestamp'], 'BUY', row['close']))

    # Sell Condition
    elif in_position and row['RSI'] > 60:
        cash = btc * row['close']
        btc = 0
        in_position = False
        trade_log.append((row['timestamp'], 'SELL', row['close']))

# Final Portfolio Value
final_value = cash if not in_position else btc * df.iloc[-1]['close']
print(f"Final Portfolio Value: ${final_value:.2f}")

# Save Trade Log
log_df = pd.DataFrame(trade_log, columns=['timestamp', 'action', 'price'])
log_df.to_csv('trade_log_rsi.csv', index=False)
print("Trade log saved to trade_log_rsi.csv ✅")

# Plot
plt.figure(figsize=(14, 7))
plt.plot(df['timestamp'], df['close'], label='BTC Price', alpha=0.5)
plt.plot(df['timestamp'], df['MA_50'], label='50-Day MA', linestyle='--')
plt.plot(df['timestamp'], df['RSI'], label='RSI (scaled)', alpha=0.3)

# Mark trades
for t, action, price in trade_log:
    color = 'green' if action == 'BUY' else 'red'
    marker = '^' if action == 'BUY' else 'v'
    plt.scatter(t, price, marker=marker, color=color, label=action, zorder=5)

plt.title('BTC/USDT – RSI Strategy with 50MA Filter')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()