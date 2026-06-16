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


def _sync_page_from_query():
    page = st.query_params.get("page")
    if page in PAGE_OPTIONS:
        st.session_state.page = page


def _set_current_page(page):
    st.session_state.page = page
    st.query_params["page"] = page
    st.rerun()


def render_sidebar_inputs():
    """Render sidebar controls and return validated app inputs."""
    _sync_page_from_query()

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-mark">
                    <span></span>
                    <strong>Quant Research</strong>
                </div>
                <p>Models, signals, and market context</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
                    _set_current_page(option)
                page = option

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

        with st.expander("Settings", expanded=False):
            st.caption("Appearance")
            theme_mode = st.selectbox(
                "Theme",
                ["System", "Dark", "Light"],
                key="theme_mode",
                help="Choose app appearance without relying on browser defaults.",
            )
            accent_mode = st.selectbox(
                "Accent",
                ["Sky", "Teal", "Violet"],
                key="accent_mode",
                help="Adjust the highlight color used across navigation and cards.",
            )
            motion_enabled = st.toggle(
                "Motion effects",
                key="motion_enabled",
                value=st.session_state.get("motion_enabled", True),
                help="Enable subtle animated emphasis across the interface.",
            )

        st.divider()
        st.caption("Current scope: educational research backtests, not live trading.")

    return {
        "page": page,
        "theme_mode": theme_mode,
        "accent_mode": accent_mode,
        "motion_enabled": motion_enabled,
        "symbol": symbol,
        "interval": interval,
        "interval_display": interval_display,
        "start_date": start_date,
        "end_date": end_date,
        "submitted": submitted,
        "is_valid": not errors,
    }
