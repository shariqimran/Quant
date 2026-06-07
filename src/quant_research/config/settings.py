"""Shared project settings and default assumptions."""

OHLCV_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]

INTERVAL_PERIODS_PER_YEAR = {
    "1d": 252,
    "1wk": 52,
    "1mo": 12,
    "3mo": 4,
    "1h": 24 * 365,
    "60m": 24 * 365,
    "30m": 24 * 365 * 2,
    "15m": 24 * 365 * 4,
    "5m": 24 * 365 * 12,
    "2m": 24 * 365 * 30,
    "1m": 24 * 365 * 60,
}

DEFAULT_PERIODS_PER_YEAR = 252


def get_interval_periods_per_year(interval: str) -> int:
    """Return annualization periods for a data interval."""
    return INTERVAL_PERIODS_PER_YEAR.get(interval, DEFAULT_PERIODS_PER_YEAR)

