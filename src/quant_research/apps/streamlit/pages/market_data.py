"""Market data inspection page."""

import streamlit as st

from src.quant_research.apps.streamlit.components.layout import render_data_summary


def render_market_data_page(df, inputs):
    """Render raw market data inspection page."""
    st.subheader("Market Data")
    st.caption(
        f"{inputs['symbol']} | {inputs['interval_display']} | "
        f"{inputs['start_date']} to {inputs['end_date']}"
    )
    render_data_summary(df)

    st.markdown("#### Price series")
    st.line_chart(df.set_index("timestamp")["close"])

    st.markdown("#### Latest rows")
    st.dataframe(df.tail(20), use_container_width=True, hide_index=True)

    st.markdown("#### Data quality")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Missing values", int(df.isna().sum().sum()))
    with col2:
        st.metric("Duplicate timestamps", int(df["timestamp"].duplicated().sum()))
    with col3:
        st.metric("Columns", len(df.columns))
