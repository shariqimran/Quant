"""Reusable Streamlit forms and parameter controls."""

import streamlit as st


def render_ma_backtest_ui(symbol, start_date, end_date):
    """Render moving-average backtest controls."""
    st.subheader("Moving Average Crossover Backtest")

    st.markdown("#### Moving averages")
    col1, col2 = st.columns(2)
    with col1:
        short_window = st.slider("Short MA Window", 5, 50, 20)
    with col2:
        long_window = st.slider("Long MA Window", 20, 200, 100)

    is_valid = short_window < long_window
    if not is_valid:
        st.error("Short MA window must be less than long MA window.")

    col1, col2, col3 = st.columns(3)
    with col1:
        backtest_symbol = st.text_input("Backtest Symbol", value=symbol, key="ma_backtest_symbol")
    with col2:
        backtest_start = st.date_input("Backtest Start Date", value=start_date, key="ma_backtest_start")
    with col3:
        backtest_end = st.date_input("Backtest End Date", value=end_date, key="ma_backtest_end")

    initial_capital = st.number_input(
        "Initial Capital ($)",
        min_value=1000,
        max_value=1000000,
        value=10000,
        step=1000,
        key="ma_backtest_capital",
    )

    return {
        "backtest_symbol": backtest_symbol,
        "backtest_start": backtest_start,
        "backtest_end": backtest_end,
        "initial_capital": initial_capital,
        "short_window": short_window,
        "long_window": long_window,
        "is_valid": is_valid,
    }


def render_volatility_analysis_ui():
    """Render volatility analysis controls."""
    st.subheader("Volatility Analysis")

    st.markdown("#### Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        fast_vol_window = st.slider("Fast Vol Window", 10, 50, 20)
    with col2:
        slow_vol_window = st.slider("Slow Vol Window", 30, 120, 60)
    with col3:
        return_type = st.selectbox("Return Type", ["log", "arith"])

    return {
        "fast_vol_window": fast_vol_window,
        "slow_vol_window": slow_vol_window,
        "return_type": return_type,
    }


def render_rsi_backtest_ui(symbol, start_date, end_date):
    """Render RSI backtest controls."""
    st.subheader("RSI Strategy Backtest")

    st.markdown("#### RSI settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        rsi_period = st.slider("RSI Period", 5, 30, 14)
    with col2:
        oversold_threshold = st.slider("Oversold Threshold", 10, 40, 30)
    with col3:
        overbought_threshold = st.slider("Overbought Threshold", 60, 90, 70)

    col1, col2, col3 = st.columns(3)
    with col1:
        backtest_symbol = st.text_input("Backtest Symbol", value=symbol, key="rsi_backtest_symbol")
    with col2:
        backtest_start = st.date_input("Backtest Start Date", value=start_date, key="rsi_backtest_start")
    with col3:
        backtest_end = st.date_input("Backtest End Date", value=end_date, key="rsi_backtest_end")

    initial_capital = st.number_input(
        "Initial Capital ($)",
        min_value=1000,
        max_value=1000000,
        value=10000,
        step=1000,
        key="rsi_backtest_capital",
    )

    return {
        "backtest_symbol": backtest_symbol,
        "backtest_start": backtest_start,
        "backtest_end": backtest_end,
        "initial_capital": initial_capital,
        "rsi_period": rsi_period,
        "oversold_threshold": oversold_threshold,
        "overbought_threshold": overbought_threshold,
    }


def render_sentiment_analysis_ui(symbol):
    """Render sentiment-analysis controls."""
    st.subheader("Sentiment Analysis")
    st.info("Experimental RSS-based sentiment. Treat the verdict as research context, not a trading signal.")

    if st.button("Analyze sentiment", key="run_sentiment_analysis"):
        return True

    return False

