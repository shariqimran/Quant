"""Tests for historical (realized) volatility helpers."""

import numpy as np
import pandas as pd

from src.quant_research.indicators.realized_volatility import latest_realized_volatility


def _make_price_series(n: int, daily_vol: float = 0.01) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    returns = rng.normal(0, daily_vol, size=n)
    close = 100 * np.exp(np.cumsum(returns))
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=n, freq="B"),
            "open": close,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": 1_000_000,
        }
    )


def test_latest_realized_volatility_returns_annualized_decimal():
    df = _make_price_series(120, daily_vol=0.012)
    vol = latest_realized_volatility(df, window=20, periods_per_year=252)
    assert vol is not None
    assert 0.05 < vol < 0.80


def test_latest_realized_volatility_insufficient_data():
    df = _make_price_series(10)
    assert latest_realized_volatility(df, window=20) is None


def test_latest_realized_volatility_uses_log_returns():
    df = _make_price_series(80)
    vol = latest_realized_volatility(df, window=30, return_type="log")
    assert vol is not None
    assert vol > 0
