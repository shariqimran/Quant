"""Shared layout blocks for the Streamlit app."""

import streamlit as st


def render_header():
    """Render the app header."""
    st.markdown('<h1 class="main-header">Quant Research Workbench</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Market data, indicators, and strategy experiments in one research view.</div>',
        unsafe_allow_html=True,
    )


def render_data_summary(df):
    """Render compact data summary metrics."""
    if df is None or df.empty:
        return

    latest_timestamp = df["timestamp"].max()
    latest_close = df["close"].iloc[-1]
    total_return = ((df["close"].iloc[-1] / df["close"].iloc[0]) - 1) * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Latest close", f"${latest_close:,.2f}")
    with col3:
        st.metric("Data return", f"{total_return:.2f}%")
    with col4:
        st.metric("Latest bar", latest_timestamp.strftime("%Y-%m-%d"))


def render_welcome_message():
    """Render a data-required empty state."""
    st.markdown(
        """
    <div class="empty-state">
        <h3>Load a market series to begin</h3>
        <p>Select a symbol, frequency, and date range in the sidebar.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.subheader("Common starting points")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Stocks**")
        st.write("AAPL, MSFT, TSLA")
    with col2:
        st.markdown("**ETFs**")
        st.write("SPY, QQQ, VTI")
    with col3:
        st.markdown("**Crypto**")
        st.write("BTC-USD, ETH-USD")

