"""Momentum indicators and signal helpers."""


def calculate_rsi(df, period=14):
    """Calculate a simple rolling-average RSI indicator."""
    df = df.copy()
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def get_rsi_signals(df, oversold_threshold=30, overbought_threshold=70):
    """Return RSI overbought and oversold signal slices."""
    df = df.copy()
    df["rsi_oversold"] = df["RSI"] < oversold_threshold
    df["rsi_overbought"] = df["RSI"] > overbought_threshold

    return {
        "oversold_periods": df[df["rsi_oversold"]].copy(),
        "overbought_periods": df[df["rsi_overbought"]].copy(),
    }

