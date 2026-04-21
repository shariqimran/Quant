import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np


@st.cache_data
def fetch_data(symbol, interval, start_date, end_date):
    """Fetch data from Yahoo Finance with caching"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)

        if df.empty:
            st.error(f"No data found for {symbol}")
            return None

        df = df.reset_index()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        date_col = (
            "Date"
            if "Date" in df.columns
            else ("Datetime" if "Datetime" in df.columns else df.columns[0])
        )

        rename_map = {
            date_col: "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
        df = df.rename(columns=rename_map)

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

        required_columns = ["timestamp", "open", "high", "low", "close", "volume"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            st.write(f"Available columns: {list(df.columns)}")
            return None

        df = df[required_columns]
        df = df.dropna(subset=["timestamp", "open", "high", "low", "close"])

        if df.empty:
            st.error(f"No data found for {symbol}")
            return None

        return df.sort_values("timestamp").reset_index(drop=True)
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        st.write("Please check if the symbol is valid and try again.")
        return None


def calculate_returns(df):
    """Calculate arithmetic and log returns"""
    df = df.copy()
    df["return_arith"] = df["close"].pct_change()
    df["return_log"] = np.log(df["close"]).diff()
    return df


def get_data_summary(df):
    """Get basic data summary statistics"""
    if df is None or df.empty:
        return None

    summary = {
        "data_points": len(df),
        "date_range": f"{df['timestamp'].min().date()} to {df['timestamp'].max().date()}",
        "current_price": df["close"].iloc[-1],
        "total_return": ((df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0]) * 100,
    }
    return summary
