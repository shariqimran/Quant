"""Historical (realized) volatility from underlying price history."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd

from src.quant_research.config.settings import DEFAULT_PERIODS_PER_YEAR, get_interval_periods_per_year
from src.quant_research.data.loaders import calculate_returns, fetch_yahoo_history

DEFAULT_HIST_VOL_WINDOWS = (20, 30, 60)
DEFAULT_LOOKBACK_DAYS = 365


@dataclass(frozen=True)
class RealizedVolatilitySnapshot:
    """Annualized realized volatility over a rolling window."""

    symbol: str
    window_days: int
    annualized_vol: float
    lookback_days: int
    start_date: str
    end_date: str
    sample_size: int
    interval: str = "1d"


def latest_realized_volatility(
    df: pd.DataFrame,
    window: int,
    *,
    return_type: str = "log",
    periods_per_year: int = DEFAULT_PERIODS_PER_YEAR,
) -> float | None:
    """
    Annualized realized vol from the latest ``window`` returns in ``df``.

    Expects a normalized OHLCV frame with a ``close`` column.
    """
    if df is None or df.empty or window < 2 or len(df) < window + 1:
        return None

    work = calculate_returns(df.copy())
    return_col = f"return_{return_type}"
    rolling_std = work[return_col].rolling(window=window).std()
    latest = rolling_std.iloc[-1]
    if latest is None or np.isnan(latest):
        return None
    return float(latest * np.sqrt(periods_per_year))


def compute_realized_volatility_profile(
    symbol: str,
    *,
    windows: tuple[int, ...] = DEFAULT_HIST_VOL_WINDOWS,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    interval: str = "1d",
    end_date: date | None = None,
) -> dict[int, RealizedVolatilitySnapshot]:
    """Fetch Yahoo history and compute realized vol for each rolling window."""
    end = end_date or date.today()
    start = end - timedelta(days=lookback_days)
    df = fetch_yahoo_history(symbol, interval, start, end)
    periods_per_year = get_interval_periods_per_year(interval)

    profile: dict[int, RealizedVolatilitySnapshot] = {}
    for window in windows:
        annualized = latest_realized_volatility(
            df,
            window,
            periods_per_year=periods_per_year,
        )
        if annualized is None:
            continue
        profile[window] = RealizedVolatilitySnapshot(
            symbol=symbol.upper(),
            window_days=window,
            annualized_vol=annualized,
            lookback_days=lookback_days,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            sample_size=len(df),
            interval=interval,
        )
    return profile
