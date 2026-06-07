"""Market data service functions for the Streamlit app."""

import streamlit as st

from src.quant_research.data.loaders import (
    calculate_returns,
    fetch_yahoo_history,
    get_data_summary,
)


@st.cache_data(ttl=600, show_spinner="Fetching data...")
def _fetch_data_cached(symbol, interval, start_date, end_date):
    """Fetch Yahoo Finance data with Streamlit caching."""
    return fetch_yahoo_history(symbol, interval, start_date, end_date)


def fetch_data(symbol, interval, start_date, end_date):
    """Fetch data from Yahoo Finance with app-friendly error reporting."""
    try:
        return _fetch_data_cached(symbol, interval, start_date, end_date)
    except Exception as exc:
        message = str(exc)
        st.error(f"Error fetching data: {message}")
        low = message.lower()
        if "too many requests" in low or "429" in message or "rate limit" in low:
            st.warning(
                "Yahoo Finance often **rate-limits shared IPs**. This failure was "
                "**not** stored in the app cache, so the next fetch will try again. "
                "Wait a few minutes, try another symbol briefly, or use the menu to clear cache."
            )
        else:
            st.caption("Check the symbol, interval, and date range. Yahoo has limits on intraday history.")
        return None
