"""Cached Yahoo Finance option and quote helpers for Streamlit."""

from __future__ import annotations

from math import isfinite

import streamlit as st
import yfinance as yf

from src.quant_research.data.options_loaders import (
    fetch_option_chain,
    fetch_option_chains,
    fetch_option_expirations,
)
from src.quant_research.indicators.realized_volatility import (
    DEFAULT_HIST_VOL_WINDOWS,
    DEFAULT_LOOKBACK_DAYS,
    RealizedVolatilitySnapshot,
    compute_realized_volatility_profile,
)


def _safe_float(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(number):
        return None
    return number


def _get_fast_info_value(fast_info, *names):
    for name in names:
        try:
            value = fast_info.get(name)
        except AttributeError:
            value = getattr(fast_info, name, None)
        if _safe_float(value) is not None or isinstance(value, str):
            return value
    return None


@st.cache_data(ttl=30, show_spinner=False)
def fetch_live_quote(symbol: str) -> dict:
    """Fetch a short-lived underlying quote snapshot."""
    ticker = yf.Ticker(symbol)
    try:
        fast_info = ticker.fast_info
    except Exception:
        fast_info = {}

    quote = {
        "price": _get_fast_info_value(fast_info, "last_price", "lastPrice"),
        "previous_close": _get_fast_info_value(
            fast_info,
            "previous_close",
            "previousClose",
            "regular_market_previous_close",
            "regularMarketPreviousClose",
        ),
        "day_high": _get_fast_info_value(fast_info, "day_high", "dayHigh"),
        "day_low": _get_fast_info_value(fast_info, "day_low", "dayLow"),
        "currency": _get_fast_info_value(fast_info, "currency") or "USD",
        "quote_time": None,
        "source": "Yahoo Finance fast_info",
    }

    if _safe_float(quote["price"]) is None:
        history = ticker.history(period="1d", interval="1m")
        clean_history = history.dropna(subset=["Close"]) if not history.empty else history
        if not clean_history.empty:
            latest = clean_history.iloc[-1]
            quote["price"] = latest["Close"]
            quote["day_high"] = history["High"].max()
            quote["day_low"] = history["Low"].min()
            quote["quote_time"] = str(clean_history.index[-1])
            quote["source"] = "Yahoo Finance 1m history"

    return quote


@st.cache_data(ttl=300, show_spinner=False)
def fetch_expirations(symbol: str) -> list[str]:
    """Listed option expiration dates for ``symbol``."""
    return fetch_option_expirations(symbol)


@st.cache_data(ttl=120, show_spinner=False)
def fetch_option_chain_cached(symbol: str, expiration: str) -> tuple:
    """Cached call/put chain for one expiration."""
    return fetch_option_chain(symbol, expiration)


@st.cache_data(ttl=120, show_spinner=False)
def fetch_option_chains_cached(symbol: str, expirations: tuple[str, ...]) -> dict[str, tuple]:
    """
    Cached multi-expiration fetch.

    ``expirations`` must be a tuple (hashable) for Streamlit cache keys.
    """
    return fetch_option_chains(symbol, list(expirations))


@st.cache_data(ttl=600, show_spinner=False)
def fetch_realized_volatility_profile(
    symbol: str,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> dict[int, RealizedVolatilitySnapshot]:
    """Cached realized-vol profile from daily Yahoo history."""
    return compute_realized_volatility_profile(
        symbol,
        windows=DEFAULT_HIST_VOL_WINDOWS,
        lookback_days=lookback_days,
        interval="1d",
    )


def clear_options_cache() -> None:
    """Clear all option/quote Streamlit caches."""
    fetch_live_quote.clear()
    fetch_expirations.clear()
    fetch_option_chain_cached.clear()
    fetch_option_chains_cached.clear()
    fetch_realized_volatility_profile.clear()
