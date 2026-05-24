"""Pure backtest calculations.

This module intentionally has no Streamlit or Plotly imports. It should stay
focused on deterministic portfolio/trade calculations that are easy to test.
"""

import numpy as np
import pandas as pd


MA_TRADE_COLUMNS = ["date", "action", "price", "shares", "capital", "portfolio_value"]
RSI_TRADE_COLUMNS = [
    "date",
    "action",
    "price",
    "rsi",
    "shares",
    "capital",
    "portfolio_value",
]


def require_columns(df, required_columns, context="backtest"):
    """Raise a ValueError when a DataFrame is missing required columns."""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns for {context}: {missing_columns}")


def run_moving_average_backtest(df, initial_capital=10000):
    """Run the current moving-average crossover backtest calculation."""
    require_columns(df, ["timestamp", "close", "ma_short", "ma_long"], "MA backtest")

    df_bt = df.copy()
    capital = initial_capital
    shares = 0
    position = 0
    trades = []

    df_bt["ma_cross"] = np.where(df_bt["ma_short"] > df_bt["ma_long"], 1, 0)
    df_bt["ma_cross_change"] = df_bt["ma_cross"].diff()

    for i in range(1, len(df_bt)):
        current_price = df_bt["close"].iloc[i]
        current_date = df_bt["timestamp"].iloc[i]

        if df_bt["ma_cross_change"].iloc[i] == 1 and position == 0:
            shares = capital / current_price
            capital = 0
            position = 1
            trades.append(
                {
                    "date": current_date,
                    "action": "BUY",
                    "price": current_price,
                    "shares": shares,
                    "capital": capital,
                    "portfolio_value": shares * current_price,
                }
            )
        elif df_bt["ma_cross_change"].iloc[i] == -1 and position == 1:
            capital = shares * current_price
            shares = 0
            position = 0
            trades.append(
                {
                    "date": current_date,
                    "action": "SELL",
                    "price": current_price,
                    "shares": shares,
                    "capital": capital,
                    "portfolio_value": capital,
                }
            )

    final_value = shares * df_bt["close"].iloc[-1] if position == 1 else capital
    log_df = pd.DataFrame(trades) if trades else pd.DataFrame(columns=MA_TRADE_COLUMNS)
    return final_value, log_df, df_bt


def run_rsi_backtest(
    df,
    initial_capital=10000,
    oversold_threshold=30,
    overbought_threshold=70,
):
    """Run the current RSI threshold backtest calculation."""
    require_columns(df, ["timestamp", "close", "RSI"], "RSI backtest")

    df_bt = df.copy()
    capital = initial_capital
    shares = 0
    position = 0
    trades = []

    for i in range(1, len(df_bt)):
        current_price = df_bt["close"].iloc[i]
        current_date = df_bt["timestamp"].iloc[i]
        current_rsi = df_bt["RSI"].iloc[i]

        if pd.isna(current_rsi):
            continue

        if current_rsi < oversold_threshold and position == 0:
            shares = capital / current_price
            capital = 0
            position = 1
            trades.append(
                {
                    "date": current_date,
                    "action": "BUY",
                    "price": current_price,
                    "rsi": current_rsi,
                    "shares": shares,
                    "capital": capital,
                    "portfolio_value": shares * current_price,
                }
            )
        elif current_rsi > overbought_threshold and position == 1:
            capital = shares * current_price
            shares = 0
            position = 0
            trades.append(
                {
                    "date": current_date,
                    "action": "SELL",
                    "price": current_price,
                    "rsi": current_rsi,
                    "shares": shares,
                    "capital": capital,
                    "portfolio_value": capital,
                }
            )

    final_value = shares * df_bt["close"].iloc[-1] if position == 1 else capital
    log_df = pd.DataFrame(trades) if trades else pd.DataFrame(columns=RSI_TRADE_COLUMNS)
    return final_value, log_df, df_bt
