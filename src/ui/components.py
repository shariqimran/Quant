import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objects as go

def setup_page_config():
    """Setup page configuration"""
    st.set_page_config(
        page_title="Quant Research Workbench",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def load_custom_css():
    """Load custom CSS styling"""
    st.markdown("""
    <style>
        header[data-testid="stHeader"] {
            background: transparent;
        }
        footer {
            visibility: hidden;
        }
        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }
        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(148, 163, 184, 0.18);
            background: #111827;
        }
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.75rem;
        }
        section[data-testid="stSidebar"] h1 {
            font-size: 1.3rem;
            letter-spacing: 0;
            margin-bottom: 0.35rem;
            color: #f8fafc;
        }
        .main-header {
            font-size: 1.58rem;
            font-weight: 750;
            color: #f8fafc;
            margin-bottom: 0.05rem;
            letter-spacing: 0;
        }
        .app-subtitle {
            color: #94a3b8;
            font-size: 0.92rem;
            margin-bottom: 1.25rem;
        }
        .hero-panel {
            border: 1px solid rgba(56, 189, 248, 0.18);
            border-radius: 12px;
            padding: 1.25rem 1.35rem;
            background:
                linear-gradient(135deg, rgba(14, 165, 233, 0.16), rgba(15, 23, 42, 0.78)),
                #111827;
            margin-bottom: 1rem;
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.18);
        }
        .hero-kicker {
            color: #38bdf8;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.04rem;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }
        .hero-title {
            color: #f8fafc;
            font-size: 1.9rem;
            font-weight: 760;
            margin: 0;
            letter-spacing: 0;
            line-height: 1.15;
        }
        .hero-subtitle {
            color: #cbd5e1;
            font-size: 0.95rem;
            margin-top: 0.55rem;
            max-width: 780px;
        }
        .kpi-card {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 10px;
            padding: 0.9rem 1rem;
            background: #111827;
            min-height: 96px;
        }
        .kpi-label {
            color: #94a3b8;
            font-size: 0.76rem;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: 0.03rem;
            margin-bottom: 0.45rem;
        }
        .kpi-value {
            color: #f8fafc;
            font-size: 1.45rem;
            font-weight: 760;
            line-height: 1.1;
            margin: 0;
        }
        .kpi-note {
            color: #94a3b8;
            font-size: 0.82rem;
            margin-top: 0.35rem;
        }
        .delta-positive {
            color: #22c55e;
        }
        .delta-negative {
            color: #f87171;
        }
        .empty-state {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 10px;
            padding: 1.35rem;
            background: #111827;
            color: #f8fafc;
            margin-bottom: 1rem;
        }
        .empty-state p {
            color: #94a3b8;
        }
        .dashboard-card {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 10px;
            padding: 1rem 1rem 0.95rem 1rem;
            background: #111827;
            min-height: 132px;
            position: relative;
            overflow: hidden;
        }
        .dashboard-card:before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 3px;
            background: #38bdf8;
            opacity: 0.9;
        }
        .dashboard-card h4 {
            margin: 0 0 0.5rem 0;
            font-size: 1rem;
            color: #f8fafc;
        }
        .dashboard-card p {
            margin: 0;
            color: #94a3b8;
            font-size: 0.88rem;
            line-height: 1.38;
        }
        .module-tag {
            display: inline-block;
            margin-top: 0.85rem;
            font-size: 0.74rem;
            color: #38bdf8;
            font-weight: 700;
        }
        .section-label {
            color: #94a3b8;
            font-size: 0.78rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.04rem;
            margin: 1.1rem 0 0.55rem 0;
        }
        .status-pill {
            display: inline-flex;
            align-items: center;
            border: 1px solid rgba(56, 189, 248, 0.30);
            border-radius: 999px;
            padding: 0.22rem 0.58rem;
            font-size: 0.78rem;
            color: #bae6fd;
            background: rgba(14, 165, 233, 0.12);
        }
        .workflow-strip {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 10px;
            padding: 0.75rem 0.85rem;
            background: #111827;
            margin-top: 0.5rem;
        }
        .workflow-step {
            color: #e5e7eb;
            font-size: 0.88rem;
            margin: 0.32rem 0;
        }
        .workflow-index {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.35rem;
            height: 1.35rem;
            border-radius: 999px;
            background: rgba(14, 165, 233, 0.18);
            color: #7dd3fc;
            font-size: 0.72rem;
            font-weight: 750;
            margin-right: 0.45rem;
        }
        div[data-testid="stMetric"] {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 8px;
            padding: 0.75rem 0.85rem;
            background: #111827;
        }
        button[kind="primary"] {
            border-radius: 7px;
            font-weight: 650;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 46px;
            white-space: pre-wrap;
            background-color: #111827;
            color: #e5e7eb;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 8px;
            padding-bottom: 8px;
        }
        .stTabs [aria-selected="true"] {
            border-bottom: 2px solid #38bdf8;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render the main header"""
    st.markdown('<h1 class="main-header">Quant Research Workbench</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Market data, indicators, and strategy experiments in one research view.</div>',
        unsafe_allow_html=True,
    )

def render_sidebar_inputs():
    """Render sidebar controls and return validated data-fetch inputs."""
    with st.sidebar:
        st.title("Quant Research")

        page = st.pills(
            "Navigation",
            ["Home", "Market Data", "Strategy Lab", "Risk & Metrics", "Sentiment", "Export"],
            default="Home",
            label_visibility="collapsed",
            width="stretch",
        )

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

            submitted = st.form_submit_button("Load data", type="primary", use_container_width=True)

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


def _format_money(value):
    return f"${value:,.2f}"


def _render_kpi_card(label, value, note="", note_class=""):
    note_markup = f'<div class="kpi-note {note_class}">{note}</div>' if note else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <p class="kpi-value">{value}</p>
            {note_markup}
        </div>
        """,
        unsafe_allow_html=True,
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
    st.plotly_chart(fig, use_container_width=True)


def render_home_page(df, inputs, has_data):
    """Render the dashboard landing page."""
    st.markdown(
        f"""
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
            _render_kpi_card("Latest close", _format_money(latest_close), delta_note, delta_class)
        with col2:
            _render_kpi_card("Range return", f"{total_return:+.2f}%", "Selected date window")
        with col3:
            _render_kpi_card("Rows loaded", f"{len(df):,}", "Cleaned OHLCV records")
        with col4:
            _render_kpi_card("Latest bar", latest_bar, "Most recent timestamp")

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
        st.markdown("""
        <div class="empty-state">
            <h3>Load a market series</h3>
            <p>Select a symbol, frequency, and date range in the sidebar. The dashboard will populate with a market snapshot and research modules.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Research Modules</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h4>Market Data</h4>
            <p>Price, volume, rows, duplicate timestamps, and missing-value checks.</p>
            <span class="module-tag">Inspect</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h4>Strategy Lab</h4>
            <p>Moving-average and RSI experiments with explicit parameters.</p>
            <span class="module-tag">Experiment</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="dashboard-card">
            <h4>Risk & Metrics</h4>
            <p>Volatility, return stats, Sharpe ratio, regimes, and drawdown context.</p>
            <span class="module-tag">Evaluate</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Workflow</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="workflow-strip">
        <div class="workflow-step"><span class="workflow-index">1</span>Load data</div>
        <div class="workflow-step"><span class="workflow-index">2</span>Inspect price and data quality</div>
        <div class="workflow-step"><span class="workflow-index">3</span>Run a strategy experiment</div>
        <div class="workflow-step"><span class="workflow-index">4</span>Evaluate risk and benchmark behavior</div>
    </div>
    """, unsafe_allow_html=True)


def render_data_summary(df):
    """Render data summary metrics"""
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
    """Render empty state before data is loaded."""
    st.markdown("""
    <div class="empty-state">
        <h3>Load a market series to begin</h3>
        <p>Select a symbol, frequency, and date range in the sidebar.</p>
    </div>
    """, unsafe_allow_html=True)

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

def render_ma_backtest_ui(symbol, start_date, end_date):
    """Render moving average backtest UI"""
    st.subheader("Moving Average Crossover Backtest")
    
    # Moving average parameters
    st.markdown("#### Moving averages")
    col1, col2 = st.columns(2)
    with col1:
        short_window = st.slider("Short MA Window", 5, 50, 20)
    with col2:
        long_window = st.slider("Long MA Window", 20, 200, 100)
    
    is_valid = short_window < long_window
    if not is_valid:
        st.error("Short MA window must be less than long MA window.")

    # User input for backtest
    col1, col2, col3 = st.columns(3)
    with col1:
        backtest_symbol = st.text_input("Backtest Symbol", value=symbol, key="ma_backtest_symbol")
    with col2:
        backtest_start = st.date_input("Backtest Start Date", value=start_date, key="ma_backtest_start")
    with col3:
        backtest_end = st.date_input("Backtest End Date", value=end_date, key="ma_backtest_end")

    initial_capital = st.number_input("Initial Capital ($)", min_value=1000, max_value=1000000, value=10000, step=1000, key="ma_backtest_capital")

    return {
        'backtest_symbol': backtest_symbol,
        'backtest_start': backtest_start,
        'backtest_end': backtest_end,
        'initial_capital': initial_capital,
        'short_window': short_window,
        'long_window': long_window,
        'is_valid': is_valid
    }

def render_volatility_analysis_ui():
    """Render volatility analysis UI with sliders"""
    st.subheader("Volatility Analysis")
    
    # Volatility parameters
    st.markdown("#### Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        fast_vol_window = st.slider("Fast Vol Window", 10, 50, 20)
    with col2:
        slow_vol_window = st.slider("Slow Vol Window", 30, 120, 60)
    with col3:
        return_type = st.selectbox("Return Type", ["log", "arith"])
    
    return {
        'fast_vol_window': fast_vol_window,
        'slow_vol_window': slow_vol_window,
        'return_type': return_type
    }

def render_rsi_backtest_ui(symbol, start_date, end_date):
    """Render RSI backtest UI"""
    st.subheader("RSI Strategy Backtest")

    # RSI parameters
    st.markdown("#### RSI settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        rsi_period = st.slider("RSI Period", 5, 30, 14)
    with col2:
        oversold_threshold = st.slider("Oversold Threshold", 10, 40, 30)
    with col3:
        overbought_threshold = st.slider("Overbought Threshold", 60, 90, 70)

    # User input for backtest
    col1, col2, col3 = st.columns(3)
    with col1:
        backtest_symbol = st.text_input("Backtest Symbol", value=symbol, key="rsi_backtest_symbol")
    with col2:
        backtest_start = st.date_input("Backtest Start Date", value=start_date, key="rsi_backtest_start")
    with col3:
        backtest_end = st.date_input("Backtest End Date", value=end_date, key="rsi_backtest_end")

    initial_capital = st.number_input("Initial Capital ($)", min_value=1000, max_value=1000000, value=10000, step=1000, key="rsi_backtest_capital")

    return {
        'backtest_symbol': backtest_symbol,
        'backtest_start': backtest_start,
        'backtest_end': backtest_end,
        'initial_capital': initial_capital,
        'rsi_period': rsi_period,
        'oversold_threshold': oversold_threshold,
        'overbought_threshold': overbought_threshold
    }

def render_sentiment_analysis_ui(symbol):
    """Render sentiment analysis UI"""
    st.subheader("Sentiment Analysis")
    st.info("Experimental RSS-based sentiment. Treat the verdict as research context, not a trading signal.")
    
    # Analysis button
    if st.button("Analyze sentiment", key="run_sentiment_analysis"):
        return True
    
    return False
