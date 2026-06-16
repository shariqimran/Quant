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
    )
    st.plotly_chart(fig, use_container_width=True)


def render_home_page(df, inputs, has_data):
    """Render the dashboard landing page."""
    st.markdown(
        """
        <section class="qa-landing-hero">
            <div class="qa-hero-copy">
                <div class="qa-eyebrow"><span></span>Live market research sandbox</div>
                <h1>Real-time trading intelligence for analysis, backtesting, and market context.</h1>
                <p>
                    QuantAlgo brings market data, technical strategies, portfolio metrics, sentiment signals,
                    and interactive visualizations into one focused Streamlit dashboard.
                </p>
                <div class="qa-hero-actions">
                    <a class="qa-button qa-button-primary" href="https://quantalgo.streamlit.app/" target="_blank" rel="noreferrer">View Live Demo</a>
                    <a class="qa-button qa-button-secondary" href="https://github.com/shariqimran/Quant" target="_blank" rel="noreferrer">View GitHub</a>
                </div>
                <div class="qa-hero-stats">
                    <div><strong>Signals</strong><span>MA, RSI, volatility</span></div>
                    <div><strong>Backtests</strong><span>PnL, win rate, drawdown</span></div>
                    <div><strong>Context</strong><span>Reddit + news sentiment</span></div>
                </div>
            </div>
            <div class="qa-dashboard-preview" aria-hidden="true">
                <div class="qa-window-bar"><i></i><i></i><i></i><span>QUANTALGO / STRATEGY LAB</span></div>
                <div class="qa-ticker-row"><span>AAPL</span><span>BTC-USD</span><span>SPY</span><span>TSLA</span></div>
                <div class="qa-chart-panel">
                    <div class="qa-panel-heading"><span>Equity curve</span><strong>+18.42%</strong></div>
                    <svg class="qa-equity-chart" viewBox="0 0 720 300">
                        <defs>
                            <linearGradient id="qa-line" x1="0" x2="1">
                                <stop offset="0%" stop-color="#51d7ff" />
                                <stop offset="55%" stop-color="#2fffb2" />
                                <stop offset="100%" stop-color="#ffcf5a" />
                            </linearGradient>
                            <linearGradient id="qa-fill" x1="0" x2="0" y1="0" y2="1">
                                <stop offset="0%" stop-color="#2fffb2" stop-opacity=".28" />
                                <stop offset="100%" stop-color="#2fffb2" stop-opacity="0" />
                            </linearGradient>
                        </defs>
                        <g class="qa-grid">
                            <path d="M40 50h640M40 105h640M40 160h640M40 215h640M40 270h640" />
                            <path d="M80 30v250M200 30v250M320 30v250M440 30v250M560 30v250M680 30v250" />
                        </g>
                        <path class="qa-chart-fill" d="M40 230 C95 218 102 155 150 166 C199 178 213 122 260 136 C310 151 333 92 385 102 C442 112 446 72 500 76 C552 80 560 42 610 54 C645 62 666 42 680 34 L680 280 L40 280 Z" />
                        <path class="qa-chart-line" pathLength="1" d="M40 230 C95 218 102 155 150 166 C199 178 213 122 260 136 C310 151 333 92 385 102 C442 112 446 72 500 76 C552 80 560 42 610 54 C645 62 666 42 680 34" />
                    </svg>
                </div>
                <div class="qa-mini-grid">
                    <div><span>Win rate</span><strong>62.8%</strong><small>RSI mean reversion</small></div>
                    <div><span>Max drawdown</span><strong>-7.6%</strong><small>Volatility adjusted</small></div>
                    <div><span>Sentiment</span><strong>0.37</strong><small>VADER composite</small></div>
                </div>
            </div>
        </section>
        <section class="qa-story-section">
            <div class="qa-story-panel">
                <div>
                <span class="qa-section-kicker">Why it exists</span>
                <h2>Trading research gets fragmented fast.</h2>
                </div>
                <p>
                    Analysts often jump between market data, indicators, spreadsheets, news, social context,
                    and portfolio performance views. QuantAlgo consolidates that exploratory loop into one
                    dashboard built for fast iteration and clear decision support.
                </p>
            </div>
        </section>
        <section class="qa-feature-section">
            <span class="qa-section-kicker">Core system</span>
            <h2>Navigate directly into the active research modules.</h2>
            <div class="qa-feature-grid">
                <a class="qa-feature-link" href="?page=Market+Data" target="_self"><article><span>01</span><h3>Market data</h3><p>Price history, volume, duplicate timestamps, and missing-value checks.</p></article></a>
                <a class="qa-feature-link" href="?page=Strategy+Lab" target="_self"><article><span>02</span><h3>Strategy lab</h3><p>Moving-average and RSI experiments with parameter controls and backtest output.</p></article></a>
                <a class="qa-feature-link" href="?page=Risk+%26+Metrics" target="_self"><article><span>03</span><h3>Risk &amp; metrics</h3><p>Returns, volatility, Sharpe ratio, drawdown, and market regime context.</p></article></a>
                <a class="qa-feature-link" href="?page=Black-Scholes" target="_self"><article><span>04</span><h3>Black-Scholes</h3><p>Option valuation, Greeks, live contract lookup, and pricing breakdowns.</p></article></a>
                <a class="qa-feature-link" href="?page=Binomial" target="_self"><article><span>05</span><h3>Binomial model</h3><p>Tree-based option pricing with step controls, Greeks, and exercise analysis.</p></article></a>
                <a class="qa-feature-link" href="?page=Sentiment" target="_self"><article><span>06</span><h3>Sentiment analysis</h3><p>Reddit and Google News context scored with VADER for market tone.</p></article></a>
            </div>
        </section>
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
                use_container_width=True,
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
