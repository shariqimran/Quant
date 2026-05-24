"""Portfolio and return performance metrics."""

import numpy as np
import pandas as pd

from src.quant_research.config.settings import get_interval_periods_per_year


def get_return_statistics(df, interval="1d"):
    """Calculate per-bar return stats and close-price max drawdown."""
    returns = df["return_log"].dropna()
    std = returns.std()
    mean = returns.mean()
    periods_per_year = get_interval_periods_per_year(interval)
    if len(returns) < 2 or not np.isfinite(std) or std == 0:
        sharpe_ratio = 0.0
        vol_pct = 0.0
    else:
        sharpe_ratio = float((mean / std) * np.sqrt(periods_per_year))
        vol_pct = float(std * 100)

    close = pd.to_numeric(df["close"], errors="coerce").dropna()
    if len(close) < 2 or close.iloc[0] == 0:
        max_drawdown = 0.0
    else:
        equity = close / close.iloc[0]
        running_max = equity.cummax()
        dd = (equity / running_max - 1.0) * 100.0
        max_drawdown = float(dd.min())

    mean_pct = float(mean * 100) if np.isfinite(mean) else 0.0

    return {
        "mean_return": mean_pct,
        "volatility": vol_pct,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
    }

