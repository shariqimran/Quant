import warnings
import pandas as pd
import numpy as np


def filter_df_utc_date_range(df, start, end):
    """Filter rows to [start, end] inclusive using UTC-aware timestamps."""
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")
    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)
    if start_dt.tzinfo is None:
        start_dt = start_dt.tz_localize("UTC")
    else:
        start_dt = start_dt.tz_convert("UTC")
    if end_dt.tzinfo is None:
        end_dt = end_dt.tz_localize("UTC")
    else:
        end_dt = end_dt.tz_convert("UTC")
    mask = (out["timestamp"] >= start_dt) & (out["timestamp"] <= end_dt)
    return out.loc[mask].reset_index(drop=True)

def suppress_warnings():
    """Suppress warnings for cleaner output"""
    warnings.filterwarnings('ignore')

def format_currency(value):
    """Format value as currency"""
    return f"${value:,.2f}"

def format_percentage(value):
    """Format value as percentage"""
    return f"{value:.2f}%"

def validate_dataframe(df, required_columns):
    """Validate DataFrame has required columns"""
    if df is None or df.empty:
        return False, "DataFrame is empty or None"
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {missing_columns}"
    
    return True, "DataFrame is valid"

def get_interval_ppy(interval):
    """Get periods per year for given interval"""
    ppy_map = {
        "1d": 252, "1wk": 52, "1mo": 12, "3mo": 4, 
        "1h": 24*365, "60m": 24*365, "15m": 24*365*4,
        "30m": 24*365*2, "5m": 24*365*12, "2m": 24*365*30, "1m": 24*365*60
    }
    return ppy_map.get(interval, 252)

def calculate_drawdown(returns):
    """Calculate maximum drawdown from returns"""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Calculate Sharpe ratio"""
    excess_returns = returns - risk_free_rate/252  # Daily risk-free rate
    return (excess_returns.mean() / returns.std()) * np.sqrt(252)
