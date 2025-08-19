import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

def moving_average_backtest(df, initial_capital=10000, symbol="UNKNOWN"):
    """
    Run a moving average crossover backtest
    
    Parameters:
    df: DataFrame with OHLCV data
    initial_capital: Starting capital
    symbol: Symbol name for display
    
    Returns:
    final_value: Final portfolio value
    log_df: DataFrame with trade log
    fig: Plotly figure with backtest results
    """
    try:
        # Ensure we have the required columns
        required_cols = ['timestamp', 'close', 'ma_short', 'ma_long']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Missing required columns for backtest: {missing_cols}")
            return None, None, None
        
        # Create a copy to avoid modifying original
        df_bt = df.copy()
        
        # Initialize variables
        capital = initial_capital
        shares = 0
        position = 0  # 0: no position, 1: long
        trades = []
        
        # Calculate moving average crossover signals
        df_bt['ma_cross'] = np.where(df_bt['ma_short'] > df_bt['ma_long'], 1, 0)
        df_bt['ma_cross_change'] = df_bt['ma_cross'].diff()
        
        # Run backtest
        for i in range(1, len(df_bt)):
            current_price = df_bt['close'].iloc[i]
            current_date = df_bt['timestamp'].iloc[i]
            
            # Check for buy signal (golden cross)
            if df_bt['ma_cross_change'].iloc[i] == 1 and position == 0:
                # Buy signal
                shares = capital / current_price
                capital = 0
                position = 1
                trades.append({
                    'date': current_date,
                    'action': 'BUY',
                    'price': current_price,
                    'shares': shares,
                    'capital': capital,
                    'portfolio_value': shares * current_price
                })
            
            # Check for sell signal (death cross)
            elif df_bt['ma_cross_change'].iloc[i] == -1 and position == 1:
                # Sell signal
                capital = shares * current_price
                shares = 0
                position = 0
                trades.append({
                    'date': current_date,
                    'action': 'SELL',
                    'price': current_price,
                    'shares': shares,
                    'capital': capital,
                    'portfolio_value': capital
                })
        
        # Calculate final portfolio value
        if position == 1:
            final_value = shares * df_bt['close'].iloc[-1]
        else:
            final_value = capital
        
        # Create trade log DataFrame
        if trades:
            log_df = pd.DataFrame(trades)
        else:
            log_df = pd.DataFrame(columns=['date', 'action', 'price', 'shares', 'capital', 'portfolio_value'])
        
        # Create backtest visualization
        fig = create_backtest_chart(df_bt, log_df, symbol, initial_capital, final_value)
        
        return final_value, log_df, fig
        
    except Exception as e:
        st.error(f"Error in backtest: {str(e)}")
        return None, None, None

def create_backtest_chart(df, log_df, symbol, initial_capital, final_value):
    """Create backtest visualization chart"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Price and Moving Averages', 'Portfolio Value'),
        vertical_spacing=0.1,
        row_heights=[0.6, 0.4]
    )
    
    # Price and moving averages
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['close'],
                  mode='lines', name='Close Price',
                  line=dict(color='#1f77b4', width=2)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['ma_short'],
                  mode='lines', name='Short MA',
                  line=dict(color='#ff7f0e', width=1.5)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['ma_long'],
                  mode='lines', name='Long MA',
                  line=dict(color='#2ca02c', width=1.5)),
        row=1, col=1
    )
    
    # Add buy/sell signals
    if not log_df.empty:
        buy_signals = log_df[log_df['action'] == 'BUY']
        sell_signals = log_df[log_df['action'] == 'SELL']
        
        if not buy_signals.empty:
            fig.add_trace(
                go.Scatter(x=buy_signals['date'], y=buy_signals['price'],
                          mode='markers', name='Buy Signal',
                          marker=dict(color='green', size=10, symbol='triangle-up')),
                row=1, col=1
            )
        
        if not sell_signals.empty:
            fig.add_trace(
                go.Scatter(x=sell_signals['date'], y=sell_signals['price'],
                          mode='markers', name='Sell Signal',
                          marker=dict(color='red', size=10, symbol='triangle-down')),
                row=1, col=1
            )
    
    # Portfolio value
    if not log_df.empty:
        fig.add_trace(
            go.Scatter(x=log_df['date'], y=log_df['portfolio_value'],
                      mode='lines+markers', name='Portfolio Value',
                      line=dict(color='purple', width=2)),
            row=2, col=1
        )
    
    # Add initial capital line
    fig.add_hline(y=initial_capital, line_dash="dash", line_color="gray",
                  annotation_text=f"Initial Capital: ${initial_capital:,.0f}", row=2, col=1)
    
    # Calculate performance metrics
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    
    fig.update_layout(
        title=f'{symbol} - Moving Average Crossover Backtest<br>'
              f'Final Value: ${final_value:,.2f} | Return: {total_return:.2f}%',
        height=700,
        showlegend=True
    )
    
    return fig
