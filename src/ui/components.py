import streamlit as st
from datetime import datetime, timedelta

def setup_page_config():
    """Setup page configuration"""
    st.set_page_config(
        page_title="Quantitative Trading Analysis",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def load_custom_css():
    """Load custom CSS styling"""
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

def render_header():
    """Render the main header"""
    st.markdown('<h1 class="main-header">📈 Quantitative Trading Analysis</h1>', unsafe_allow_html=True)

def render_sidebar_inputs():
    """Render sidebar inputs"""
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
        

        
        # Fetch data button
        if st.button("🚀 Fetch & Analyze Data", type="primary"):
            st.session_state.fetch_data = True
    
    return {
        'symbol': symbol,
        'interval': interval,
        'start_date': start_date,
        'end_date': end_date
    }

def render_data_summary(df):
    """Render data summary metrics"""
    if df is None or df.empty:
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Data Points", len(df))
    with col2:
        st.metric("Date Range", f"{df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
    with col3:
        st.metric("Current Price", f"${df['close'].iloc[-1]:.2f}")

def render_welcome_message():
    """Render welcome message when no data is loaded"""
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

def render_ma_backtest_ui(symbol, start_date, end_date):
    """Render moving average backtest UI"""
    st.subheader("Moving Average Crossover Backtest")
    st.markdown("""
    This backtest simulates a simple moving average crossover strategy:
    - **Buy** when the short MA crosses above the long MA
    - **Sell** when the short MA crosses below the long MA
    """)
    
    # Moving average parameters
    st.header("📈 Moving Averages")
    col1, col2 = st.columns(2)
    with col1:
        short_window = st.slider("Short MA Window", 5, 50, 20)
    with col2:
        long_window = st.slider("Long MA Window", 20, 200, 100)
    
    # Show current values
    st.info(f"Current settings: Short MA = {short_window} days, Long MA = {long_window} days")
    st.info("Uses yfinance data. For best results, use daily interval and a long enough date range.")

    # User input for backtest
    col1, col2, col3 = st.columns(3)
    with col1:
        backtest_symbol = st.text_input("Backtest Symbol", value=symbol, key="ma_backtest_symbol")
    with col2:
        backtest_start = st.date_input("Backtest Start Date", value=start_date, key="ma_backtest_start")
    with col3:
        backtest_end = st.date_input("Backtest End Date", value=end_date, key="ma_backtest_end")

    initial_capital = st.number_input("Initial Capital ($)", min_value=1000, max_value=1000000, value=10000, step=1000, key="ma_backtest_capital")

    return {
        'backtest_symbol': backtest_symbol,
        'backtest_start': backtest_start,
        'backtest_end': backtest_end,
        'initial_capital': initial_capital,
        'short_window': short_window,
        'long_window': long_window
    }

def render_volatility_analysis_ui():
    """Render volatility analysis UI with sliders"""
    st.subheader("Volatility Analysis")
    
    # Volatility parameters
    st.header("📊 Volatility Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        fast_vol_window = st.slider("Fast Vol Window", 10, 50, 20)
    with col2:
        slow_vol_window = st.slider("Slow Vol Window", 30, 120, 60)
    with col3:
        return_type = st.selectbox("Return Type", ["log", "arith"])
    
    # Show current values
    st.info(f"Current settings: Fast Vol = {fast_vol_window} days, Slow Vol = {slow_vol_window} days, Return Type = {return_type}")
    
    return {
        'fast_vol_window': fast_vol_window,
        'slow_vol_window': slow_vol_window,
        'return_type': return_type
    }

def render_rsi_backtest_ui(symbol, start_date, end_date):
    """Render RSI backtest UI"""
    st.subheader("RSI Strategy Backtest")
    st.markdown("""
    This backtest simulates an RSI-based trading strategy:
    - **Buy** when RSI falls below the oversold threshold
    - **Sell** when RSI rises above the overbought threshold
    """)
    st.info("Uses yfinance data. For best results, use daily interval and a long enough date range.")

    # RSI parameters
    st.header("🔄 RSI Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        rsi_period = st.slider("RSI Period", 5, 30, 14)
    with col2:
        oversold_threshold = st.slider("Oversold Threshold", 10, 40, 30)
    with col3:
        overbought_threshold = st.slider("Overbought Threshold", 60, 90, 70)

    # User input for backtest
    col1, col2, col3 = st.columns(3)
    with col1:
        backtest_symbol = st.text_input("Backtest Symbol", value=symbol, key="rsi_backtest_symbol")
    with col2:
        backtest_start = st.date_input("Backtest Start Date", value=start_date, key="rsi_backtest_start")
    with col3:
        backtest_end = st.date_input("Backtest End Date", value=end_date, key="rsi_backtest_end")

    initial_capital = st.number_input("Initial Capital ($)", min_value=1000, max_value=1000000, value=10000, step=1000, key="rsi_backtest_capital")

    return {
        'backtest_symbol': backtest_symbol,
        'backtest_start': backtest_start,
        'backtest_end': backtest_end,
        'initial_capital': initial_capital,
        'rsi_period': rsi_period,
        'oversold_threshold': oversold_threshold,
        'overbought_threshold': overbought_threshold
    }

def render_sentiment_analysis_ui(symbol):
    """Render sentiment analysis UI"""
    st.subheader("Sentiment Analysis")
    st.markdown("""
    This analysis fetches and analyzes sentiment from Reddit and Google News sources:
    - **Reddit**: Searches r/stocks, r/investing, r/wallstreetbets, r/CryptoCurrency
    - **Google News**: Searches for recent news articles
    - **VADER Sentiment**: Analyzes text sentiment using VADER (Valence Aware Dictionary and sEntiment Reasoner)
    """)
    st.info("This may take a few moments to fetch and analyze the latest posts and news.")
    
    # Analysis button
    if st.button("🔍 Analyze Sentiment", key="run_sentiment_analysis"):
        return True
    
    return False
