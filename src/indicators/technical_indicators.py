import pandas as pd
import numpy as np

def calculate_moving_averages(df, short_window, long_window):
    """Calculate moving averages"""
    df = df.copy()
    df['ma_short'] = df['close'].rolling(window=short_window).mean()
    df['ma_long'] = df['close'].rolling(window=long_window).mean()
    return df

def calculate_volatility(df, window, return_type='log', interval='1d'):
    """Calculate rolling volatility"""
    df = df.copy()
    
    # Periods per year mapping
    ppy_map = {
        "1d": 252, "1wk": 52, "1mo": 12, "3mo": 4, 
        "1h": 24*365, "60m": 24*365, "15m": 24*365*4,
        "30m": 24*365*2, "5m": 24*365*12, "2m": 24*365*30, "1m": 24*365*60
    }
    PPY = ppy_map.get(interval, 252)
    
    # Calculate volatility
    return_col = f'return_{return_type}'
    if return_col not in df.columns:
        if return_type == 'log':
            df['return_log'] = np.log(df['close']).diff()
        else:
            df['return_arith'] = df['close'].pct_change()
    
    df[f'volatility_{window}'] = df[return_col].rolling(window=window).std() * np.sqrt(PPY)
    return df

def calculate_rsi(df, period=14):
    """Calculate RSI indicator"""
    df = df.copy()
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def get_moving_average_signals(df):
    """Get moving average crossover signals"""
    df = df.copy()
    df['ma_cross'] = np.where(df['ma_short'] > df['ma_long'], 1, 0)
    df['ma_cross_change'] = df['ma_cross'].diff()
    
    crossovers = df[df['ma_cross_change'] != 0].copy()
    
    signals = {
        'golden_crosses': crossovers[crossovers['ma_cross_change'] == 1],
        'death_crosses': crossovers[crossovers['ma_cross_change'] == -1],
        'all_crossovers': crossovers
    }
    
    return signals

def get_rsi_signals(df, oversold_threshold=30, overbought_threshold=70):
    """Get RSI overbought/oversold signals"""
    df = df.copy()
    df['rsi_oversold'] = df['RSI'] < oversold_threshold
    df['rsi_overbought'] = df['RSI'] > overbought_threshold
    
    signals = {
        'oversold_periods': df[df['rsi_oversold']].copy(),
        'overbought_periods': df[df['rsi_overbought']].copy()
    }
    
    return signals

def get_volatility_summary_stats(df, fast_window, slow_window):
    """Calculate volatility summary statistics"""
    fast_vol = df[f'volatility_{fast_window}'].dropna()
    slow_vol = df[f'volatility_{slow_window}'].dropna()
    
    # Calculate thresholds
    low_thr = fast_vol.quantile(0.25)
    high_thr = fast_vol.quantile(0.75)
    
    # Calculate regime coverage
    share_low = (fast_vol < low_thr).mean()
    share_high = (fast_vol > high_thr).mean()
    share_mid = 1 - share_low - share_high
    
    stats = {
        'fast_mean': fast_vol.mean(),
        'fast_median': fast_vol.median(),
        'fast_95p': fast_vol.quantile(0.95),
        'slow_mean': slow_vol.mean(),
        'slow_median': slow_vol.median(),
        'slow_95p': slow_vol.quantile(0.95),
        'low_threshold': low_thr,
        'high_threshold': high_thr,
        'share_low': share_low,
        'share_high': share_high,
        'share_mid': share_mid
    }
    
    return stats

def get_return_statistics(df):
    """Calculate return statistics"""
    returns = df['return_log'].dropna()
    
    stats = {
        'mean_return': returns.mean() * 100,
        'volatility': returns.std() * 100,
        'sharpe_ratio': (returns.mean() / returns.std()) * np.sqrt(252),
        'max_drawdown': returns.cumsum().min() * 100
    }
    
    return stats
