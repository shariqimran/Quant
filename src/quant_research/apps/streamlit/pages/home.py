"""Home dashboard page."""

import plotly.graph_objects as go
import streamlit as st

from src.quant_research.apps.streamlit.components.cards import (
    format_money,
    render_kpi_card,
)


def _render_home_price_chart(df, symbol):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["close"],
            mode="lines",
            name="Close",
            line=dict(color="#22c55e", width=2.2),
            fill="tozeroy",
            fillcolor="rgba(34, 197, 94, 0.10)",
            hovertemplate="%{x}<br>Close: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"{symbol} close price",
        height=310,
        margin=dict(l=8, r=8, t=44, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.18)"),
        font=dict(size=12, color="#cbd5e1"),
        title_font=dict(color="#f8fafc", size=15),
    )
    st.plotly_chart(fig, width="stretch")


def render_home_page(df, inputs, has_data):
    """Render the dashboard landing page."""
    st.markdown(
        """
        <div class="hero-panel">
            <div class="hero-kicker">Modern Quant Dashboard</div>
            <h2 class="hero-title">Research, test, and explain market strategies.</h2>
            <div class="hero-subtitle">
                A focused workspace for loading market data, inspecting signals, and moving toward realistic backtests.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if has_data:
        latest_close = df["close"].iloc[-1]
        previous_close = df["close"].iloc[-2] if len(df) > 1 else latest_close
        day_change = latest_close - previous_close
        day_change_pct = (day_change / previous_close) * 100 if previous_close else 0
        total_return = ((latest_close / df["close"].iloc[0]) - 1) * 100 if df["close"].iloc[0] else 0
        latest_bar = df["timestamp"].max().strftime("%Y-%m-%d")
        range_label = f"{inputs['start_date']} to {inputs['end_date']}"
        delta_class = "delta-positive" if day_change_pct >= 0 else "delta-negative"
        delta_note = f"{day_change:+,.2f} ({day_change_pct:+.2f}%) last bar"

        st.markdown(
            f'<span class="status-pill">{inputs["symbol"]} | {inputs["interval_display"]} | {range_label}</span>',
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_kpi_card("Latest close", format_money(latest_close), delta_note, delta_class)
        with col2:
            render_kpi_card("Range return", f"{total_return:+.2f}%", "Selected date window")
        with col3:
            render_kpi_card("Rows loaded", f"{len(df):,}", "Cleaned OHLCV records")
        with col4:
            render_kpi_card("Latest bar", latest_bar, "Most recent timestamp")

        left, right = st.columns([1.7, 1])
        with left:
            st.markdown('<div class="section-label">Market Snapshot</div>', unsafe_allow_html=True)
            _render_home_price_chart(df, inputs["symbol"])
        with right:
            st.markdown('<div class="section-label">Recent Bars</div>', unsafe_allow_html=True)
            st.dataframe(
                df[["timestamp", "open", "high", "low", "close", "volume"]].tail(7),
                width="stretch",
                hide_index=True,
                height=310,
            )
    else:
        st.markdown(
            """
        <div class="empty-state">
            <h3>Load a market series</h3>
            <p>Select a symbol, frequency, and date range in the sidebar. The dashboard will populate with a market snapshot and research modules.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">Research Modules</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
        <div class="dashboard-card">
            <h4>Market Data</h4>
            <p>Price, volume, rows, duplicate timestamps, and missing-value checks.</p>
            <span class="module-tag">Inspect</span>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
        <div class="dashboard-card">
            <h4>Strategy Lab</h4>
            <p>Moving-average and RSI experiments with explicit parameters.</p>
            <span class="module-tag">Experiment</span>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
        <div class="dashboard-card">
            <h4>Risk & Metrics</h4>
            <p>Volatility, return stats, Sharpe ratio, regimes, and drawdown context.</p>
            <span class="module-tag">Evaluate</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-label">Workflow</div>', unsafe_allow_html=True)
    st.markdown(
        """
    <div class="workflow-strip">
        <div class="workflow-step"><span class="workflow-index">1</span>Load data</div>
        <div class="workflow-step"><span class="workflow-index">2</span>Inspect price and data quality</div>
        <div class="workflow-step"><span class="workflow-index">3</span>Run a strategy experiment</div>
        <div class="workflow-step"><span class="workflow-index">4</span>Evaluate risk and benchmark behavior</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
