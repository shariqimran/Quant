"""Risk, metrics, and volatility pages."""

import streamlit as st

from src.quant_research.indicators import (
    calculate_volatility,
    get_volatility_summary_stats,
)
from src.quant_research.apps.streamlit.components.forms import render_volatility_analysis_ui
from src.quant_research.metrics import get_return_statistics
from src.quant_research.visualization.market_charts import (
    plot_volatility,
    plot_volatility_distribution,
    plot_volatility_regimes,
)


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
    st.plotly_chart(fig, width="stretch")

    st.subheader("Volatility Regimes")
    fig = plot_volatility_regimes(
        df_vol, inputs["symbol"], vol_inputs["fast_vol_window"], vol_inputs["slow_vol_window"]
    )
    st.plotly_chart(fig, width="stretch")

    st.subheader("Volatility Distribution")
    fig = plot_volatility_distribution(
        df_vol, vol_inputs["fast_vol_window"], vol_inputs["slow_vol_window"], inputs["symbol"]
    )
    st.plotly_chart(fig, width="stretch")


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
