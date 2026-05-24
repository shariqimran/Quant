"""Volatility indicators and summary helpers."""

import numpy as np

from src.quant_research.config.settings import get_interval_periods_per_year


def calculate_volatility(df, window, return_type="log", interval="1d"):
    """Calculate annualized rolling volatility for a return column."""
    df = df.copy()
    periods_per_year = get_interval_periods_per_year(interval)

    return_col = f"return_{return_type}"
    if return_col not in df.columns:
        if return_type == "log":
            df["return_log"] = np.log(df["close"]).diff()
        else:
            df["return_arith"] = df["close"].pct_change()

    df[f"volatility_{window}"] = df[return_col].rolling(window=window).std() * np.sqrt(periods_per_year)
    return df


def get_volatility_summary_stats(df, fast_window, slow_window):
    """Calculate summary statistics for fast and slow volatility columns."""
    fast_vol = df[f"volatility_{fast_window}"].dropna()
    slow_vol = df[f"volatility_{slow_window}"].dropna()

    low_thr = fast_vol.quantile(0.25)
    high_thr = fast_vol.quantile(0.75)

    share_low = (fast_vol < low_thr).mean()
    share_high = (fast_vol > high_thr).mean()
    share_mid = 1 - share_low - share_high

    return {
        "fast_mean": fast_vol.mean(),
        "fast_median": fast_vol.median(),
        "fast_95p": fast_vol.quantile(0.95),
        "slow_mean": slow_vol.mean(),
        "slow_median": slow_vol.median(),
        "slow_95p": slow_vol.quantile(0.95),
        "low_threshold": low_thr,
        "high_threshold": high_thr,
        "share_low": share_low,
        "share_high": share_high,
        "share_mid": share_mid,
    }

