"""Backtest runner functions that combine pure engine output with charts."""

from src.quant_research.backtesting.engine import (
    run_moving_average_backtest,
    run_rsi_backtest,
)
from src.quant_research.visualization.backtest_charts import (
    create_moving_average_backtest_chart,
    create_rsi_backtest_chart,
)


def moving_average_backtest(df, initial_capital=10000, symbol="UNKNOWN"):
    """Run the current MA backtest and return final value, trade log, and chart."""
    final_value, log_df, df_bt = run_moving_average_backtest(df, initial_capital)
    fig = create_moving_average_backtest_chart(
        df_bt,
        log_df,
        symbol,
        initial_capital,
        final_value,
    )
    return final_value, log_df, fig


def rsi_backtest(
    df,
    initial_capital=10000,
    symbol="UNKNOWN",
    rsi_period=14,
    oversold_threshold=30,
    overbought_threshold=70,
):
    """Run the current RSI backtest and return final value, trade log, and chart."""
    final_value, log_df, df_bt = run_rsi_backtest(
        df,
        initial_capital=initial_capital,
        oversold_threshold=oversold_threshold,
        overbought_threshold=overbought_threshold,
    )
    fig = create_rsi_backtest_chart(
        df_bt,
        log_df,
        symbol,
        initial_capital,
        final_value,
        oversold_threshold,
        overbought_threshold,
    )
    return final_value, log_df, fig
