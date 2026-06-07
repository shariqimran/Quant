"""Streamlit page routing."""

import streamlit as st

from src.quant_research.apps.streamlit.components.layout import render_welcome_message
from src.quant_research.apps.streamlit.pages.black_scholes import render_black_scholes_page
from src.quant_research.apps.streamlit.pages.export import render_export_page
from src.quant_research.apps.streamlit.pages.home import render_home_page
from src.quant_research.apps.streamlit.pages.market_data import render_market_data_page
from src.quant_research.apps.streamlit.pages.risk_metrics import (
    render_risk_metrics_page,
    render_volatility_page,
)
from src.quant_research.apps.streamlit.pages.sentiment import render_sentiment_page
from src.quant_research.apps.streamlit.pages.strategy_lab import render_strategy_lab_page


def _require_data(df):
    """Show a data-required state and return whether data exists."""
    if df is not None:
        return True
    render_welcome_message()
    return False


def render_current_page(page, df, inputs):
    """Render the currently selected page."""
    has_data = df is not None

    if page == "Home":
        render_home_page(df, inputs, has_data)
    elif page == "Market Data" and _require_data(df):
        render_market_data_page(df, inputs)
    elif page == "Strategy Lab" and _require_data(df):
        render_strategy_lab_page(df, inputs)
    elif page == "Risk & Metrics" and _require_data(df):
        render_volatility_page(df, inputs)
        st.divider()
        render_risk_metrics_page(df, inputs)
    elif page == "Black-Scholes":
        render_black_scholes_page(inputs)
    elif page == "Sentiment":
        render_sentiment_page(inputs)
    elif page == "Export" and _require_data(df):
        render_export_page(df, inputs)
