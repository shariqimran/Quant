"""Strategy lab page."""

import streamlit as st

from src.quant_research.indicators import (
    calculate_moving_averages,
    calculate_rsi,
)
from src.quant_research.apps.streamlit.components.forms import (
    render_ma_backtest_ui,
    render_rsi_backtest_ui,
)
from src.quant_research.backtesting.runners import moving_average_backtest, rsi_backtest
from src.quant_research.utils import filter_df_utc_date_range


def _backtest_symbol_mismatch(backtest_symbol: str, loaded_symbol: str) -> bool:
    bt = (backtest_symbol or "").strip().upper()
    ld = (loaded_symbol or "").strip().upper()
    return bool(bt) and bt != ld


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
        _render_moving_average_backtest(df, inputs)
    else:
        _render_rsi_backtest(df, inputs)


def _render_moving_average_backtest(df, inputs):
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


def _render_rsi_backtest(df, inputs):
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
