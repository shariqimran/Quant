"""Market data loading and normalization."""

import numpy as np
import pandas as pd
import yfinance as yf

from src.quant_research.config.settings import OHLCV_COLUMNS


def fetch_yahoo_history(symbol, interval, start_date, end_date):
    """
    Fetch Yahoo Finance OHLCV data and return a normalized DataFrame.

    The output schema is:
    timestamp, open, high, low, close, volume
    """
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start_date, end=end_date, interval=interval)

    if df.empty:
        raise RuntimeError(f"No data returned for {symbol} (empty response).")

    df = df.reset_index()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    date_col = (
        "Date"
        if "Date" in df.columns
        else ("Datetime" if "Datetime" in df.columns else df.columns[0])
    )

    df = df.rename(
        columns={
            date_col: "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )

    if "Adj Close" in df.columns:
        df["close"] = df["Adj Close"]

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)
    else:
        df["volume"] = 0

    for col in ("open", "high", "low", "close"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    missing_columns = [col for col in OHLCV_COLUMNS if col not in df.columns]
    if missing_columns:
        raise RuntimeError(
            f"Missing required columns: {missing_columns}. Available: {list(df.columns)}"
        )

    df = df[OHLCV_COLUMNS]
    df = df.dropna(subset=["timestamp", "open", "high", "low", "close"])

    if df.empty:
        raise RuntimeError(f"No usable rows after cleaning for {symbol}.")

    return df.sort_values("timestamp").reset_index(drop=True)


def calculate_returns(df):
    """Add arithmetic and log return columns to market data."""
    df = df.copy()
    df["return_arith"] = df["close"].pct_change()
    df["return_log"] = np.log(df["close"]).diff()
    return df


def get_data_summary(df):
    """Return a small summary dictionary for normalized OHLCV data."""
    if df is None or df.empty:
        return None

    return {
        "data_points": len(df),
        "date_range": f"{df['timestamp'].min().date()} to {df['timestamp'].max().date()}",
        "current_price": df["close"].iloc[-1],
        "total_return": ((df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0]) * 100,
    }

