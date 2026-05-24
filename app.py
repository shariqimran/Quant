import streamlit as st
import pandas as pd

# Import our modular components
from src.ui.components import (
    setup_page_config,
    load_custom_css,
    render_header,
    render_sidebar_inputs,
    render_home_page,
    render_data_summary,
    render_welcome_message,
    render_ma_backtest_ui,
    render_volatility_analysis_ui,
    render_rsi_backtest_ui,
    render_sentiment_analysis_ui,
)
from src.data.data_fetcher import fetch_data, calculate_returns
from src.indicators.technical_indicators import (
    calculate_moving_averages,
    calculate_volatility,
    calculate_rsi,
    get_volatility_summary_stats,
    get_return_statistics,
)
from src.visualization.charts import (
    plot_volatility,
    plot_volatility_regimes,
    plot_volatility_distribution,
)
from src.strategies.backtest import moving_average_backtest, rsi_backtest
from src.sentiment.sentiment_analyzer import analyze_symbol
from src.utils.helpers import suppress_warnings, filter_df_utc_date_range

# Suppress warnings
suppress_warnings()


def _backtest_symbol_mismatch(backtest_symbol: str, loaded_symbol: str) -> bool:
    bt = (backtest_symbol or "").strip().upper()
    ld = (loaded_symbol or "").strip().upper()
    return bool(bt) and bt != ld


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


def _require_data(df):
    """Show a data-required state and return whether data exists."""
    if df is not None:
        return True
    render_welcome_message()
    return False


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


def render_volatility_page(df, inputs):
    """Render volatility analysis page."""
    vol_inputs = render_volatility_analysis_ui()

    df_vol = df.copy()
    df_vol = calculate_volatility(
        df_vol, vol_inputs["fast_vol_window"], vol_inputs["return_type"], inputs["interval"]
    )
    df_vol = calculate_volatility(
        df_vol, vol_inputs["slow_vol_window"], vol_inputs["return_type"], inputs["interval"]
    )

    fig = plot_volatility(
        df_vol,
        inputs["symbol"],
        vol_inputs["fast_vol_window"],
        vol_inputs["slow_vol_window"],
        vol_inputs["return_type"],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Volatility Regimes")
    fig = plot_volatility_regimes(
        df_vol, inputs["symbol"], vol_inputs["fast_vol_window"], vol_inputs["slow_vol_window"]
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Volatility Distribution")
    fig = plot_volatility_distribution(
        df_vol, vol_inputs["fast_vol_window"], vol_inputs["slow_vol_window"], inputs["symbol"]
    )
    st.plotly_chart(fig, use_container_width=True)


def render_strategy_lab_page(df, inputs):
    """Render strategy experiment page."""
    st.subheader("Strategy Lab")
    strategy = st.radio(
        "Strategy",
        ["Moving Average Crossover", "RSI Mean Reversion"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if strategy == "Moving Average Crossover":
        backtest_inputs = render_ma_backtest_ui(inputs["symbol"], inputs["start_date"], inputs["end_date"])

        if st.button("Run MA Backtest", key="run_ma_backtest"):
            with st.spinner("Running backtest..."):
                df_bt = df.copy()
                if _backtest_symbol_mismatch(backtest_inputs["backtest_symbol"], inputs["symbol"]):
                    st.warning("Backtest symbol must match loaded data. Please fetch data for the desired symbol first.")
                    final_value, log_df, fig = None, None, None
                elif not backtest_inputs["is_valid"]:
                    final_value, log_df, fig = None, None, None
                else:
                    df_bt = calculate_moving_averages(
                        df_bt, backtest_inputs["short_window"], backtest_inputs["long_window"]
                    )
                    df_bt = filter_df_utc_date_range(
                        df_bt, backtest_inputs["backtest_start"], backtest_inputs["backtest_end"]
                    )
                    final_value, log_df, fig = moving_average_backtest(
                        df_bt,
                        initial_capital=backtest_inputs["initial_capital"],
                        symbol=backtest_inputs["backtest_symbol"],
                    )

            if final_value is None:
                st.error("Backtest failed. Not enough data or invalid symbol/date range.")
            else:
                st.success(f"Final Portfolio Value: ${final_value:,.2f}")
                st.plotly_chart(fig, use_container_width=True)
                st.subheader("Trade Log")
                st.dataframe(log_df, use_container_width=True)

    else:
        rsi_inputs = render_rsi_backtest_ui(inputs["symbol"], inputs["start_date"], inputs["end_date"])

        if st.button("Run RSI Backtest", key="run_rsi_backtest"):
            with st.spinner("Running RSI backtest..."):
                df_bt = df.copy()
                if _backtest_symbol_mismatch(rsi_inputs["backtest_symbol"], inputs["symbol"]):
                    st.warning("Backtest symbol must match loaded data. Please fetch data for the desired symbol first.")
                    final_value, log_df, fig = None, None, None
                else:
                    df_bt = calculate_rsi(df_bt, rsi_inputs["rsi_period"])
                    df_bt = filter_df_utc_date_range(
                        df_bt, rsi_inputs["backtest_start"], rsi_inputs["backtest_end"]
                    )
                    final_value, log_df, fig = rsi_backtest(
                        df_bt,
                        initial_capital=rsi_inputs["initial_capital"],
                        symbol=inputs["symbol"],
                        rsi_period=rsi_inputs["rsi_period"],
                        oversold_threshold=rsi_inputs["oversold_threshold"],
                        overbought_threshold=rsi_inputs["overbought_threshold"],
                    )

            if final_value is None:
                st.error("RSI backtest failed. Not enough data or invalid symbol/date range.")
            else:
                st.success(f"Final Portfolio Value: ${final_value:,.2f}")
                st.plotly_chart(fig, use_container_width=True)
                st.subheader("Trade Log")
                st.dataframe(log_df, use_container_width=True)


def render_risk_metrics_page(df, inputs):
    """Render risk and summary statistics page."""
    st.subheader("Risk & Metrics")

    fast_vol_window = 20
    slow_vol_window = 60
    return_type = "log"

    df_summary = df.copy()
    df_summary = calculate_volatility(df_summary, fast_vol_window, return_type, inputs["interval"])
    df_summary = calculate_volatility(df_summary, slow_vol_window, return_type, inputs["interval"])

    vol_stats = get_volatility_summary_stats(df_summary, fast_vol_window, slow_vol_window)
    return_stats = get_return_statistics(df, inputs["interval"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mean return", f"{return_stats['mean_return']:.4f}%")
    with col2:
        st.metric("Volatility", f"{return_stats['volatility']:.4f}%")
    with col3:
        st.metric("Sharpe ratio", f"{return_stats['sharpe_ratio']:.3f}")
    with col4:
        st.metric("Max drawdown", f"{return_stats['max_drawdown']:.2f}%")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Volatility Summary")
        st.metric("Fast Vol Mean", f"{vol_stats['fast_mean']:.3f}")
        st.metric("Fast Vol Median", f"{vol_stats['fast_median']:.3f}")
        st.metric("Fast Vol 95th Percentile", f"{vol_stats['fast_95p']:.3f}")
        st.metric("Slow Vol Mean", f"{vol_stats['slow_mean']:.3f}")
    with col2:
        st.markdown("#### Regime Coverage")
        st.metric("Low Vol Regime (<25%)", f"{vol_stats['share_low']*100:.1f}%")
        st.metric("Normal Regime", f"{vol_stats['share_mid']*100:.1f}%")
        st.metric("High Vol Regime (>75%)", f"{vol_stats['share_high']*100:.1f}%")
        st.metric("High Vol Threshold", f"{vol_stats['high_threshold']:.3f}")


def render_sentiment_page(inputs):
    """Render sentiment analysis page."""
    should_analyze = render_sentiment_analysis_ui(inputs["symbol"])

    if should_analyze:
        with st.spinner("Fetching and analyzing sentiment data..."):
            try:
                sentiment_result = analyze_symbol(inputs["symbol"])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Verdict", sentiment_result["verdict"])
                with col2:
                    st.metric("Confidence", f"{sentiment_result['confidence']:.2f}")
                with col3:
                    st.metric("Volume", sentiment_result["metrics"].get("V", 0))

                st.subheader("Sentiment Metrics")
                metrics = sentiment_result["metrics"]
                if metrics:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Sentiment Score", f"{metrics.get('S', 0):.3f}")
                    with col2:
                        st.metric("Breadth", f"{metrics.get('breadth', 0):.3f}")
                    with col3:
                        st.metric("Intensity", f"{metrics.get('intensity', 0):.3f}")
                    with col4:
                        st.metric("Volume", metrics.get("V", 0))

                if sentiment_result["reasons"]:
                    st.subheader("Top Sentiment Sources")
                    for i, reason in enumerate(sentiment_result["reasons"], 1):
                        with st.expander(f"Source {i}: {reason['src']} (Score: {reason['score']:.3f})"):
                            st.write(f"**Excerpt:** {reason['excerpt']}")
                            st.write(f"**Link:** [{reason['link']}]({reason['link']})")

            except Exception as e:
                st.error(f"Error analyzing sentiment: {str(e)}")
                st.info("This might be due to network issues or rate limiting. Please try again later.")


def render_export_page(df, inputs):
    """Render export page."""
    st.subheader("Export")
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download processed data",
        data=csv,
        file_name=f"{inputs['symbol']}_{inputs['interval']}_{inputs['start_date']}_{inputs['end_date']}_processed.csv",
        mime="text/csv",
    )

    st.markdown("#### Preview")
    st.dataframe(df.head(20), use_container_width=True)

    st.markdown("#### Data information")
    st.write(f"**Shape:** {df.shape}")
    st.write(f"**Columns:** {list(df.columns)}")
    st.write("**Missing Values:**")
    st.write(df.isna().sum())


def main():
    """Main application function"""
    # Setup page configuration and styling
    setup_page_config()
    load_custom_css()

    # Render header
    render_header()

    # Get user inputs from sidebar
    inputs = render_sidebar_inputs()

    df = None
    if st.session_state.get("fetch_data") and inputs["is_valid"]:
        df = _load_market_data(inputs)
        if df is None:
            st.error("Failed to fetch data. Please check your symbol and try again.")

    page = inputs["page"]
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
    elif page == "Sentiment":
        render_sentiment_page(inputs)
    elif page == "Export" and _require_data(df):
        render_export_page(df, inputs)


if __name__ == "__main__":
    main()
