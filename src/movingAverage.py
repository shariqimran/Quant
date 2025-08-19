import pandas as pd
import yfinance as yf
import plotly.graph_objects as go



def moving_average_backtest(df, initial_capital=10000, symbol=None):
    """
    Run a moving average crossover backtest for a given DataFrame (already fetched OHLCV data).
    Returns final value, trade log DataFrame, and a Plotly figure.
    """
    # Defensive copy
    df = df.copy().reset_index(drop=True)


    # --- Robust column standardization for both yfinance and ccxt/old formats ---
    col_map = {}
    if 'timestamp' in df.columns:
        col_map['timestamp'] = 'Date'
    if 'close' in df.columns:
        col_map['close'] = 'Close'
    if 'open' in df.columns:
        col_map['open'] = 'Open'
    if 'high' in df.columns:
        col_map['high'] = 'High'
    if 'low' in df.columns:
        col_map['low'] = 'Low'
    if 'volume' in df.columns:
        col_map['volume'] = 'Volume'
    if col_map:
        df.rename(columns=col_map, inplace=True)


    # Ensure the date column is always named 'Date'
    if 'Date' not in df.columns:
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df.rename(columns={col: 'Date'}, inplace=True)
                break


    # Remove duplicate columns, keep first occurrence
    df = df.loc[:, ~df.columns.duplicated()]
    if 'Close' not in df.columns or 'Date' not in df.columns or len(df) < 60:
        return None, None, None



    # Calculate moving averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()


    # Drop rows where any SMA is NaN (ensures valid index access in loop)
    df = df.dropna(subset=['SMA_20', 'SMA_50']).reset_index(drop=True)

    # Initialize trading simulation
    cash = initial_capital
    asset = 0
    in_position = False
    buy_price = 0
    trade_log = []

    # Strategy loop
    for i in range(1, len(df)):
        # Use .at for scalar access (index is now guaranteed to be integer)
        prev_sma20 = df.at[i-1, 'SMA_20']
        prev_sma50 = df.at[i-1, 'SMA_50']
        curr_sma20 = df.at[i, 'SMA_20']
        curr_sma50 = df.at[i, 'SMA_50']
        curr_close = df.at[i, 'Close']
        curr_date = df.at[i, 'Date']

        # Check for crossover (20 crosses above 50)
        if not in_position and prev_sma20 < prev_sma50 and curr_sma20 > curr_sma50:
            # Buy signal
            asset = cash / curr_close
            buy_price = curr_close
            cash = 0
            in_position = True
            trade_log.append((curr_date, 'BUY', buy_price))

        # Check for crossunder (20 crosses below 50)
        elif in_position and prev_sma20 > prev_sma50 and curr_sma20 < curr_sma50:
            # Sell signal
            cash = asset * curr_close
            sell_price = curr_close
            asset = 0
            in_position = False
            trade_log.append((curr_date, 'SELL', sell_price))

    # Final portfolio value
    final_value = cash if not in_position else asset * df.iloc[-1]['Close']

    # Trade log DataFrame
    log_df = pd.DataFrame(trade_log, columns=['timestamp', 'action', 'price'])

    # Plotly visualization
    fig = go.Figure()
    plot_name = f'{symbol} Price' if symbol is not None else 'Price'
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Close'],
        mode='lines', name=plot_name,
        line=dict(color='#1f77b4', width=2),
        opacity=0.5
    ))
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['SMA_20'],
        mode='lines', name='SMA 20',
        line=dict(color='#ff7f0e', width=1.5)
    ))
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['SMA_50'],
        mode='lines', name='SMA 50',
        line=dict(color='#2ca02c', width=1.5)
    ))
    # Mark buy/sell points
    buys = log_df[log_df['action'] == 'BUY']
    sells = log_df[log_df['action'] == 'SELL']
    fig.add_trace(go.Scatter(
        x=buys['timestamp'], y=buys['price'],
        mode='markers', name='Buy',
        marker=dict(symbol='triangle-up', color='green', size=12),
        showlegend=True
    ))
    fig.add_trace(go.Scatter(
        x=sells['timestamp'], y=sells['price'],
        mode='markers', name='Sell',
        marker=dict(symbol='triangle-down', color='red', size=12),
        showlegend=True
    ))

    fig.update_layout(
        title=f'{symbol} - Moving Average Crossover Strategy' if symbol is not None else 'Moving Average Crossover Strategy',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        hovermode='x unified',
        height=500
    )

    return final_value, log_df, fig

# Example usage:
# moving_average_backtest('BTC-USD', '2022-01-01', '2025-08-18')
