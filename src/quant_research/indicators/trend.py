"""Trend-following indicators and signal helpers."""

import numpy as np


def calculate_moving_averages(df, short_window, long_window):
    """Calculate short and long simple moving averages from close prices."""
    df = df.copy()
    df["ma_short"] = df["close"].rolling(window=short_window).mean()
    df["ma_long"] = df["close"].rolling(window=long_window).mean()
    return df


def get_moving_average_signals(df):
    """Return moving-average crossover signal slices."""
    df = df.copy()
    df["ma_cross"] = np.where(df["ma_short"] > df["ma_long"], 1, 0)
    df["ma_cross_change"] = df["ma_cross"].diff()

    crossovers = df[df["ma_cross_change"] != 0].copy()

    return {
        "golden_crosses": crossovers[crossovers["ma_cross_change"] == 1],
        "death_crosses": crossovers[crossovers["ma_cross_change"] == -1],
        "all_crossovers": crossovers,
    }

