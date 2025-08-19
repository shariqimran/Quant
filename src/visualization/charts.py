import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

def plot_price_with_ma(df, symbol, short_window, long_window):
    """Plot price with moving averages"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['close'],
        mode='lines', name='Close Price',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['ma_short'],
        mode='lines', name=f'MA {short_window}',
        line=dict(color='#ff7f0e', width=1.5)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['ma_long'],
        mode='lines', name=f'MA {long_window}',
        line=dict(color='#2ca02c', width=1.5)
    ))
    
    fig.update_layout(
        title=f'{symbol.upper()} - Price with Moving Averages',
        xaxis_title='Date',
        yaxis_title='Price',
        hovermode='x unified',
        height=500
    )
    
    return fig

def plot_volatility(df, symbol, fast_window, slow_window, return_type='log'):
    """Plot volatility with fast and slow windows"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df[f'volatility_{fast_window}'],
        mode='lines', name=f'Fast Vol ({fast_window})',
        line=dict(color='#d62728', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df[f'volatility_{slow_window}'],
        mode='lines', name=f'Slow Vol ({slow_window})',
        line=dict(color='#9467bd', width=2)
    ))
    
    # Add threshold lines
    fast_vol = df[f'volatility_{fast_window}'].dropna()
    low_thr = fast_vol.quantile(0.25)
    high_thr = fast_vol.quantile(0.75)
    
    fig.add_hline(y=low_thr, line_dash="dash", line_color="blue", 
                  annotation_text=f"Low Vol Threshold (25%): {low_thr:.3f}")
    fig.add_hline(y=high_thr, line_dash="dash", line_color="red", 
                  annotation_text=f"High Vol Threshold (75%): {high_thr:.3f}")
    
    fig.update_layout(
        title=f'{symbol.upper()} - Rolling Volatility (Annualized)',
        xaxis_title='Date',
        yaxis_title='Volatility (Annualized)',
        hovermode='x unified',
        height=500
    )
    
    return fig

def plot_volatility_regimes(df, symbol, fast_window, slow_window):
    """Plot volatility with regime shading"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Volatility with Regimes', 'Binary Regime Signal'),
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Calculate thresholds
    fast_vol = df[f'volatility_{fast_window}'].dropna()
    low_thr = fast_vol.quantile(0.25)
    high_thr = fast_vol.quantile(0.75)
    
    # Create regime masks
    low_vol_mask = df[f'volatility_{fast_window}'] < low_thr
    high_vol_mask = df[f'volatility_{fast_window}'] > high_thr
    
    # Add volatility traces
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df[f'volatility_{fast_window}'],
                  mode='lines', name=f'Fast Vol ({fast_window})',
                  line=dict(color='#d62728', width=2)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df[f'volatility_{slow_window}'],
                  mode='lines', name=f'Slow Vol ({slow_window})',
                  line=dict(color='#9467bd', width=2)),
        row=1, col=1
    )
    
    # Add threshold lines
    fig.add_hline(y=low_thr, line_dash="dash", line_color="blue", 
                  annotation_text=f"Low: {low_thr:.3f}", row=1, col=1)
    fig.add_hline(y=high_thr, line_dash="dash", line_color="red", 
                  annotation_text=f"High: {high_thr:.3f}", row=1, col=1)
    
    # Add regime shading
    for i in range(len(df)):
        if low_vol_mask.iloc[i]:
            fig.add_vrect(x0=df['timestamp'].iloc[i], x1=df['timestamp'].iloc[i],
                         fillcolor="blue", opacity=0.1, layer="below", line_width=0, row=1, col=1)
        elif high_vol_mask.iloc[i]:
            fig.add_vrect(x0=df['timestamp'].iloc[i], x1=df['timestamp'].iloc[i],
                         fillcolor="red", opacity=0.1, layer="below", line_width=0, row=1, col=1)
    
    # Add binary regime signal
    regime = np.zeros(len(df))
    regime[low_vol_mask] = -1
    regime[high_vol_mask] = 1
    
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=regime,
                  mode='lines', name='Regime Signal',
                  line=dict(color='black', width=2)),
        row=2, col=1
    )
    
    fig.update_yaxes(tickvals=[-1, 0, 1], ticktext=['Low', 'Normal', 'High'], row=2, col=1)
    
    fig.update_layout(
        title=f'{symbol.upper()} - Volatility Regimes',
        height=700,
        showlegend=True
    )
    
    return fig

def plot_rsi(df, symbol):
    """Plot RSI indicator"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['RSI'],
        mode='lines', name='RSI',
        line=dict(color='#8c564b', width=2)
    ))
    
    # Add overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", 
                  annotation_text="Overbought (70)")
    fig.add_hline(y=30, line_dash="dash", line_color="green", 
                  annotation_text="Oversold (30)")
    fig.add_hline(y=50, line_dash="dot", line_color="gray", 
                  annotation_text="Neutral (50)")
    
    fig.update_layout(
        title=f'{symbol.upper()} - RSI Indicator',
        xaxis_title='Date',
        yaxis_title='RSI',
        yaxis=dict(range=[0, 100]),
        hovermode='x unified',
        height=500
    )
    
    return fig

def plot_volatility_distribution(df, fast_window, slow_window, symbol):
    """Plot volatility distribution"""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f'Fast Vol Distribution (w={fast_window})', 
                       f'Slow Vol Distribution (w={slow_window})')
    )
    
    fast_vol = df[f'volatility_{fast_window}'].dropna()
    slow_vol = df[f'volatility_{slow_window}'].dropna()
    
    fig.add_trace(
        go.Histogram(x=fast_vol, nbinsx=50, name='Fast Vol',
                    marker_color='#d62728', opacity=0.7),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Histogram(x=slow_vol, nbinsx=50, name='Slow Vol',
                    marker_color='#9467bd', opacity=0.7),
        row=1, col=2
    )
    
    fig.update_layout(
        title=f'{symbol.upper()} - Volatility Distributions',
        height=500,
        showlegend=False
    )
    
    return fig
