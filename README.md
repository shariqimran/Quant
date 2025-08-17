# Quant
Quantitative trading strategies and backtesting framework for cryptocurrency markets.

## Strategies

This project implements and backtests various technical analysis strategies for cryptocurrency trading.

### RSI (Relative Strength Index) Strategy

**What it is:** A mean reversion strategy that identifies overbought and oversold conditions in the market.

**Why it's used:** RSI is one of the most popular momentum oscillators in technical analysis. It helps traders identify potential reversal points when an asset has moved too far in one direction, making it useful for both trending and ranging markets.

**Strategy Logic:**
- **Buy Signal:** RSI < 30 (oversold) AND price above 50-day moving average (uptrend confirmation)
- **Sell Signal:** RSI > 70 (overbought)

**RSI Formula:**
```
RSI = 100 - (100 / (1 + RS))
where RS = Average Gain / Average Loss
```

**Implementation:** `src/rsi.py`

### Moving Average Crossover Strategy

**What it is:** A trend-following strategy that uses the crossover of two moving averages to generate buy and sell signals.

**Why it's used:** Moving average crossovers are widely used because they help identify trend changes and filter out market noise. They work well in trending markets and provide clear entry/exit signals.

**Strategy Logic:**
- **Buy Signal:** 20-day SMA crosses above 50-day SMA (golden cross)
- **Sell Signal:** 20-day SMA crosses below 50-day SMA (death cross)

**Moving Average Formula:**
```
SMA = (P₁ + P₂ + ... + Pₙ) / n
where P = Price, n = Period
```

**Implementation:** `src/backtest.py`

## Project Structure

- `src/` - Strategy implementations and backtesting scripts
- `data/` - Historical price data
- `trade_logs/` - Generated trade logs from backtests
