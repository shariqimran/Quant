"""Plotly chart builders for backtest outputs."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_moving_average_backtest_chart(df, log_df, symbol, initial_capital, final_value):
    """Create the moving-average backtest visualization chart."""
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Price and Moving Averages", "Portfolio Value"),
        vertical_spacing=0.1,
        row_heights=[0.6, 0.4],
    )

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["close"],
            mode="lines",
            name="Close Price",
            line=dict(color="#1f77b4", width=2),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["ma_short"],
            mode="lines",
            name="Short MA",
            line=dict(color="#ff7f0e", width=1.5),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["ma_long"],
            mode="lines",
            name="Long MA",
            line=dict(color="#2ca02c", width=1.5),
        ),
        row=1,
        col=1,
    )

    if not log_df.empty:
        buy_signals = log_df[log_df["action"] == "BUY"]
        sell_signals = log_df[log_df["action"] == "SELL"]

        if not buy_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=buy_signals["date"],
                    y=buy_signals["price"],
                    mode="markers",
                    name="Buy Signal",
                    marker=dict(color="green", size=10, symbol="triangle-up"),
                ),
                row=1,
                col=1,
            )

        if not sell_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=sell_signals["date"],
                    y=sell_signals["price"],
                    mode="markers",
                    name="Sell Signal",
                    marker=dict(color="red", size=10, symbol="triangle-down"),
                ),
                row=1,
                col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=log_df["date"],
                y=log_df["portfolio_value"],
                mode="lines+markers",
                name="Portfolio Value",
                line=dict(color="purple", width=2),
            ),
            row=2,
            col=1,
        )

    fig.add_hline(
        y=initial_capital,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Initial Capital: ${initial_capital:,.0f}",
        row=2,
        col=1,
    )

    total_return = ((final_value - initial_capital) / initial_capital) * 100
    fig.update_layout(
        title=f"{symbol} - Moving Average Crossover Backtest<br>"
        f"Final Value: ${final_value:,.2f} | Return: {total_return:.2f}%",
        height=700,
        showlegend=True,
    )

    return fig


def create_rsi_backtest_chart(
    df,
    log_df,
    symbol,
    initial_capital,
    final_value,
    oversold_threshold,
    overbought_threshold,
):
    """Create the RSI backtest visualization chart."""
    fig = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=("Price", "RSI", "Portfolio Value"),
        vertical_spacing=0.1,
        row_heights=[0.4, 0.3, 0.3],
    )

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["close"],
            mode="lines",
            name="Close Price",
            line=dict(color="#1f77b4", width=2),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["RSI"],
            mode="lines",
            name="RSI",
            line=dict(color="#8c564b", width=2),
        ),
        row=2,
        col=1,
    )

    fig.add_hline(
        y=oversold_threshold,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Oversold ({oversold_threshold})",
        row=2,
        col=1,
    )
    fig.add_hline(
        y=overbought_threshold,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Overbought ({overbought_threshold})",
        row=2,
        col=1,
    )

    if not log_df.empty:
        buy_signals = log_df[log_df["action"] == "BUY"]
        sell_signals = log_df[log_df["action"] == "SELL"]

        if not buy_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=buy_signals["date"],
                    y=buy_signals["price"],
                    mode="markers",
                    name="Buy Signal",
                    marker=dict(color="green", size=10, symbol="triangle-up"),
                ),
                row=1,
                col=1,
            )

        if not sell_signals.empty:
            fig.add_trace(
                go.Scatter(
                    x=sell_signals["date"],
                    y=sell_signals["price"],
                    mode="markers",
                    name="Sell Signal",
                    marker=dict(color="red", size=10, symbol="triangle-down"),
                ),
                row=1,
                col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=log_df["date"],
                y=log_df["portfolio_value"],
                mode="lines+markers",
                name="Portfolio Value",
                line=dict(color="purple", width=2),
            ),
            row=3,
            col=1,
        )

    fig.add_hline(
        y=initial_capital,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Initial Capital: ${initial_capital:,.0f}",
        row=3,
        col=1,
    )

    total_return = ((final_value - initial_capital) / initial_capital) * 100
    fig.update_layout(
        title=f"{symbol} - RSI Strategy Backtest<br>"
        f"Final Value: ${final_value:,.2f} | Return: {total_return:.2f}%",
        height=800,
        showlegend=True,
    )
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
    fig.update_yaxes(title_text="Portfolio Value", row=3, col=1)

    return fig
