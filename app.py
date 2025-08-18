import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Quantitative Trading Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def fetch_data(symbol, interval, start_date, end_date):
    """Fetch data from Yahoo Finance with caching"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval)
        
        if df.empty:
            st.error(f"No data found for {symbol}")
            return None
            
        # Reset index to get timestamp as a column
        df = df.reset_index()
        
        # Check what columns we actually have (debug info)
        # st.write(f"Debug: Available columns: {list(df.columns)}")
        
        # Handle different column structures
        if 'Adj Close' in df.columns:
            # For stocks with adjusted close
            df = df.rename(columns={
                'Date': 'timestamp',
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Adj Close': 'adj_close',
                'Volume': 'volume'
            })
            # Use adjusted close as the main close price
            df['close'] = df['adj_close']
            df = df.drop('adj_close', axis=1)
        else:
            # For crypto or other assets without adjusted close
            df = df.rename(columns={
                'Date': 'timestamp',
                'Open': 'open',
                'High': 'high',
                'Low': 'low', 
                'Close': 'close',
                'Volume': 'volume'
            })
        
        # Keep only the columns we need
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        # Verify all required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            st.write(f"Available columns: {list(df.columns)}")
            return None
            
        df = df[required_columns]
        
        return df.sort_values('timestamp').reset_index(drop=True)
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        st.write("Please check if the symbol is valid and try again.")
        return None

def calculate_returns(df):
    """Calculate arithmetic and log returns"""
    df = df.copy()
    df['return_arith'] = df['close'].pct_change()
    df['return_log'] = np.log(df['close']).diff()
    return df

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

def get_summary_stats(df, fast_window, slow_window):
    """Calculate summary statistics"""
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

# Main app
def main():
    st.markdown('<h1 class="main-header">📈 Quantitative Trading Analysis</h1>', unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📊 Data Inputs")
        
        # Symbol input
        symbol = st.text_input("Symbol (e.g., AAPL, BTC-USD, TSLA)", value="AAPL").upper()
        
        # Interval selection
        interval_options = {
            "1 Day": "1d",
            "1 Week": "1wk", 
            "1 Month": "1mo",
            "1 Hour": "1h",
            "30 Minutes": "30m",
            "15 Minutes": "15m",
            "5 Minutes": "5m"
        }
        interval_display = st.selectbox("Interval", list(interval_options.keys()))
        interval = interval_options[interval_display]
        
        # Date range
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())
        
        # Moving average parameters
        st.header("📈 Moving Averages")
        short_window = st.slider("Short MA Window", 5, 50, 20)
        long_window = st.slider("Long MA Window", 20, 200, 100)
        
        # Volatility parameters
        st.header("📊 Volatility Settings")
        fast_vol_window = st.slider("Fast Vol Window", 10, 50, 20)
        slow_vol_window = st.slider("Slow Vol Window", 30, 120, 60)
        return_type = st.selectbox("Return Type", ["log", "arith"])
        
        # Fetch data button
        if st.button("🚀 Fetch & Analyze Data", type="primary"):
            st.session_state.fetch_data = True
    
    # Main content area
    if 'fetch_data' in st.session_state and st.session_state.fetch_data:
        with st.spinner("Fetching data..."):
            df = fetch_data(symbol, interval, start_date, end_date)
        
        if df is not None:
            # Calculate all indicators
            df = calculate_returns(df)
            df = calculate_moving_averages(df, short_window, long_window)
            df = calculate_volatility(df, fast_vol_window, return_type, interval)
            df = calculate_volatility(df, slow_vol_window, return_type, interval)
            df = calculate_rsi(df)
            
            # Display basic info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Data Points", len(df))
            with col2:
                st.metric("Date Range", f"{df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
            with col3:
                st.metric("Current Price", f"${df['close'].iloc[-1]:.2f}")
            with col4:
                price_change = ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
                st.metric("Total Return", f"{price_change:.2f}%")
            
            # Create tabs for different analyses
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📈 Price & Moving Averages", 
                "📊 Volatility Analysis", 
                "🔄 RSI Analysis",
                "📋 Summary Statistics",
                "📁 Data Export"
            ])
            
            with tab1:
                st.subheader("Price Chart with Moving Averages")
                fig = plot_price_with_ma(df, symbol, short_window, long_window)
                st.plotly_chart(fig, use_container_width=True)
                
                # Moving average crossover analysis
                st.subheader("Moving Average Crossover Analysis")
                df['ma_cross'] = np.where(df['ma_short'] > df['ma_long'], 1, 0)
                df['ma_cross_change'] = df['ma_cross'].diff()
                
                crossovers = df[df['ma_cross_change'] != 0].copy()
                if not crossovers.empty:
                    st.write("**Golden Crosses (Buy Signals):**")
                    golden_crosses = crossovers[crossovers['ma_cross_change'] == 1]
                    if not golden_crosses.empty:
                        st.dataframe(golden_crosses[['timestamp', 'close']].head(10))
                    
                    st.write("**Death Crosses (Sell Signals):**")
                    death_crosses = crossovers[crossovers['ma_cross_change'] == -1]
                    if not death_crosses.empty:
                        st.dataframe(death_crosses[['timestamp', 'close']].head(10))
                else:
                    st.info("No moving average crossovers found in the selected period.")
            
            with tab2:
                st.subheader("Volatility Analysis")
                
                # Volatility chart
                fig = plot_volatility(df, symbol, fast_vol_window, slow_vol_window, return_type)
                st.plotly_chart(fig, use_container_width=True)
                
                # Volatility regimes
                st.subheader("Volatility Regimes")
                fig = plot_volatility_regimes(df, symbol, fast_vol_window, slow_vol_window)
                st.plotly_chart(fig, use_container_width=True)
                
                # Volatility distribution
                st.subheader("Volatility Distribution")
                fig = plot_volatility_distribution(df, fast_vol_window, slow_vol_window, symbol)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.subheader("RSI Analysis")
                fig = plot_rsi(df, symbol)
                st.plotly_chart(fig, use_container_width=True)
                
                # RSI signals
                st.subheader("RSI Signals")
                df['rsi_oversold'] = df['RSI'] < 30
                df['rsi_overbought'] = df['RSI'] > 70
                
                oversold_periods = df[df['rsi_oversold']].copy()
                overbought_periods = df[df['rsi_overbought']].copy()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Oversold Periods (RSI < 30):**")
                    if not oversold_periods.empty:
                        st.dataframe(oversold_periods[['timestamp', 'close', 'RSI']].head(10))
                    else:
                        st.info("No oversold periods found.")
                
                with col2:
                    st.write("**Overbought Periods (RSI > 70):**")
                    if not overbought_periods.empty:
                        st.dataframe(overbought_periods[['timestamp', 'close', 'RSI']].head(10))
                    else:
                        st.info("No overbought periods found.")
            
            with tab4:
                st.subheader("Summary Statistics")
                
                # Volatility summary
                stats = get_summary_stats(df, fast_vol_window, slow_vol_window)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**📊 Volatility Summary (Annualized)**")
                    st.metric("Fast Vol Mean", f"{stats['fast_mean']:.3f}")
                    st.metric("Fast Vol Median", f"{stats['fast_median']:.3f}")
                    st.metric("Fast Vol 95th Percentile", f"{stats['fast_95p']:.3f}")
                    st.metric("Slow Vol Mean", f"{stats['slow_mean']:.3f}")
                    st.metric("Slow Vol Median", f"{stats['slow_median']:.3f}")
                    st.metric("Slow Vol 95th Percentile", f"{stats['slow_95p']:.3f}")
                
                with col2:
                    st.markdown("**📈 Regime Coverage**")
                    st.metric("Low Vol Regime (<25%)", f"{stats['share_low']*100:.1f}%")
                    st.metric("Normal Regime", f"{stats['share_mid']*100:.1f}%")
                    st.metric("High Vol Regime (>75%)", f"{stats['share_high']*100:.1f}%")
                    st.metric("Low Vol Threshold", f"{stats['low_threshold']:.3f}")
                    st.metric("High Vol Threshold", f"{stats['high_threshold']:.3f}")
                
                # Return statistics
                st.subheader("Return Statistics")
                returns = df['return_log'].dropna()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mean Return", f"{returns.mean()*100:.4f}%")
                with col2:
                    st.metric("Volatility", f"{returns.std()*100:.4f}%")
                with col3:
                    st.metric("Sharpe Ratio", f"{(returns.mean()/returns.std())*np.sqrt(252):.3f}")
                with col4:
                    st.metric("Max Drawdown", f"{(returns.cumsum().min())*100:.2f}%")
            
            with tab5:
                st.subheader("Data Export")
                
                # Download processed data
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Processed Data (CSV)",
                    data=csv,
                    file_name=f"{symbol}_{interval}_{start_date}_{end_date}_processed.csv",
                    mime="text/csv"
                )
                
                # Display data preview
                st.subheader("Data Preview")
                st.dataframe(df.head(10))
                
                # Data info
                st.subheader("Data Information")
                st.write(f"**Shape:** {df.shape}")
                st.write(f"**Columns:** {list(df.columns)}")
                st.write(f"**Missing Values:**")
                st.write(df.isna().sum())
        
        else:
            st.error("Failed to fetch data. Please check your symbol and try again.")
    
    else:
        # Welcome message
        st.markdown("""
        ## Welcome to Quantitative Trading Analysis! 🚀
        
        This application provides comprehensive technical analysis tools for financial markets:
        
        ### 📊 **Features:**
        - **Real-time data fetching** from Yahoo Finance
        - **Moving Average Analysis** with customizable windows
        - **Volatility Analysis** with regime detection
        - **RSI Indicator** with overbought/oversold signals
        - **Interactive charts** with Plotly
        - **Summary statistics** and export capabilities
        
        ### 🎯 **How to use:**
        1. Enter a symbol (e.g., AAPL, BTC-USD, TSLA)
        2. Select your preferred interval and date range
        3. Adjust moving average and volatility parameters
        4. Click "Fetch & Analyze Data" to start
        5. Explore different tabs for various analyses
        
        ### 💡 **Pro Tips:**
        - Use **daily data** for most reliable backtesting
        - **RSI < 30** suggests oversold conditions (potential buy)
        - **RSI > 70** suggests overbought conditions (potential sell)
        - **Golden Cross** (short MA > long MA) = bullish signal
        - **Death Cross** (short MA < long MA) = bearish signal
        """)
        
        # Example symbols
        st.subheader("📋 Popular Symbols")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Stocks:**")
            st.write("- AAPL (Apple)")
            st.write("- TSLA (Tesla)")
            st.write("- GOOGL (Google)")
        with col2:
            st.write("**Crypto:**")
            st.write("- BTC-USD (Bitcoin)")
            st.write("- ETH-USD (Ethereum)")
            st.write("- ADA-USD (Cardano)")
        with col3:
            st.write("**ETFs:**")
            st.write("- SPY (S&P 500)")
            st.write("- QQQ (NASDAQ)")
            st.write("- VTI (Total Market)")

if __name__ == "__main__":
    main()
