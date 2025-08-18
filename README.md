# Quant
Quantitative trading strategies and backtesting framework for cryptocurrency markets.

## Strategies

This project implements and backtests various technical analysis strategies for cryptocurrency trading.

## Supported Data Intervals (Yahoo Finance via `yfinance`)

When fetching data with `fetch_data_yf`, you can choose how often price/volume is sampled. This is controlled by the **`interval`** parameter.

| Interval     | Meaning             | Typical Use Case                   | Availability (Yahoo)            |
|--------------|---------------------|------------------------------------|---------------------------------|
| `1m`         | 1 minute            | High-frequency trading experiments | Up to ~60 days back             |
| `2m`         | 2 minutes           | Short-term intraday analysis       | Up to ~60 days back             |
| `5m`         | 5 minutes           | Intraday backtests                 | Up to ~60 days back             |
| `15m`        | 15 minutes          | Swing trading, short intraday      | Up to ~60 days back             |
| `30m`        | 30 minutes          | Low-frequency intraday             | Up to ~60 days back             |
| `60m` / `1h` | 1 hour              | Intraday with less noise           | Up to ~60 days back             |
| `1d`         | 1 day               | Standard backtesting & analysis    | Up to ~20+ years back           |
| `1wk`        | 1 week              | Long-term trend analysis           | Full history                    |
| `1mo`        | 1 month             | Long-term investing, portfolio sims| Full history                    |
| `3mo`        | 3 months (quarterly)| Macro/quarterly reporting cycles   | Full history                    |

### Notes
- Yahoo limits **minute-level intervals (`1m` → `60m`)** to the past ~60 days.  
- **Daily or higher (`1d`, `1wk`, `1mo`, `3mo`)** can go back decades depending on the asset.  
- For **backtests**, start with `1d` or higher — intraday data has more quirks and requires more cleaning.  
- Stocks often include an **`Adj Close`** column (adjusted for dividends/splits). In our pipeline, we standardize this into `close`.

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

## Web Application

This project includes a **Streamlit web application** that provides an interactive interface for quantitative analysis.

### 🚀 **Quick Start**

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the web app:**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** and navigate to `http://localhost:8501`

### 📊 **Web App Features**

- **Real-time data fetching** from Yahoo Finance
- **Interactive parameter adjustment** with sliders and dropdowns
- **Multiple analysis tabs:**
  - Price & Moving Averages
  - Volatility Analysis with regime detection
  - RSI Analysis with overbought/oversold signals
  - Summary Statistics
  - Data Export
- **Interactive Plotly charts** with zoom, pan, and hover functionality
- **Data export capabilities** (CSV download)

### 🎯 **How to Use the Web App**

1. **Enter a symbol** (e.g., AAPL, BTC-USD, TSLA)
2. **Select interval** and date range
3. **Adjust parameters** for moving averages and volatility
4. **Click "Fetch & Analyze Data"**
5. **Explore different tabs** for various analyses

## Project Structure

- `src/` - Strategy implementations and backtesting scripts
- `data/` - Historical price data
- `trade_logs/` - Generated trade logs from backtests
- `app.py` - Streamlit web application
- `requirements.txt` - Python dependencies
