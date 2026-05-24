"""Main Streamlit application shell."""

import streamlit as st

from src.quant_research.apps.streamlit.components.layout import render_header
from src.quant_research.apps.streamlit.components.sidebar import render_sidebar_inputs
from src.quant_research.apps.streamlit.components.styles import (
    load_custom_css,
    setup_page_config,
)
from src.quant_research.apps.streamlit.router import render_current_page
from src.quant_research.apps.streamlit.services.market_data import calculate_returns, fetch_data
from src.quant_research.utils import suppress_warnings


def _load_market_data(inputs):
    """Fetch and enrich market data for the selected sidebar inputs."""
    with st.spinner("Fetching data..."):
        df = fetch_data(
            inputs["symbol"],
            inputs["interval"],
            inputs["start_date"],
            inputs["end_date"],
        )
    if df is None:
        return None
    return calculate_returns(df)


def main():
    """Run the Streamlit app."""
    suppress_warnings()
    setup_page_config()
    load_custom_css()
    render_header()

    inputs = render_sidebar_inputs()

    df = None
    if st.session_state.get("fetch_data") and inputs["is_valid"]:
        df = _load_market_data(inputs)
        if df is None:
            st.error("Failed to fetch data. Please check your symbol and try again.")

    render_current_page(inputs["page"], df, inputs)
