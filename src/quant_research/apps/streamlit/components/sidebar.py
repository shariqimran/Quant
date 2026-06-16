"""Sidebar navigation and market-data controls."""

from datetime import datetime, timedelta

import streamlit as st


PAGE_OPTIONS = [
    "Home",
    "Market Data",
    "Strategy Lab",
    "Risk & Metrics",
    "Black-Scholes",
    "Binomial",
    "Sentiment",
    "Export",
]


def render_sidebar_inputs():
    """Render sidebar controls and return validated app inputs."""
    with st.sidebar:
        st.title("Quant Research")
        st.caption("Navigation")
        page = st.session_state.get("page", "Home")
        if page not in PAGE_OPTIONS:
            page = "Home"
            st.session_state.page = page

        for option in PAGE_OPTIONS:
            if st.button(
                option,
                key=f"nav_{option.lower().replace(' ', '_').replace('&', 'and').replace('-', '_')}",
                type="primary" if page == option else "secondary",
                width="stretch",
            ):
                if st.session_state.get("page") != option:
                    st.session_state.page = option
                    st.rerun()
                page = option

        st.divider()

        interval_options = {
            "1 day": "1d",
            "1 week": "1wk",
            "1 month": "1mo",
            "1 hour": "1h",
            "30 minutes": "30m",
            "15 minutes": "15m",
            "5 minutes": "5m",
        }

        with st.form("market_data_form"):
            st.subheader("Market data")
            symbol = st.text_input("Symbol", value="AAPL", help="Examples: AAPL, SPY, BTC-USD").strip().upper()
            interval_display = st.selectbox("Frequency", list(interval_options.keys()))
            interval = interval_options[interval_display]

            st.subheader("Date range")
            default_end = datetime.now().date()
            default_start = default_end - timedelta(days=365)
            start_date = st.date_input("Start", value=default_start)
            end_date = st.date_input("End", value=default_end)

            submitted = st.form_submit_button("Load data", type="primary", width="stretch")

        errors = []
        if not symbol:
            errors.append("Enter a ticker symbol.")
        if start_date >= end_date:
            errors.append("Start date must be before end date.")

        for error in errors:
            st.error(error)

        if submitted and not errors:
            st.session_state.fetch_data = True
        elif submitted:
            st.session_state.fetch_data = False

        st.divider()
        st.caption("Current scope: educational research backtests, not live trading.")

    return {
        "page": page,
        "symbol": symbol,
        "interval": interval,
        "interval_display": interval_display,
        "start_date": start_date,
        "end_date": end_date,
        "submitted": submitted,
        "is_valid": not errors,
    }
