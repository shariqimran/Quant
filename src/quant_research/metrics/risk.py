"""Risk metric helpers."""

import numpy as np


def calculate_drawdown(returns):
    """Calculate maximum drawdown from a return series."""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Calculate a daily-return Sharpe ratio using a simple annual risk-free assumption."""
    excess_returns = returns - risk_free_rate / 252
    return (excess_returns.mean() / returns.std()) * np.sqrt(252)

