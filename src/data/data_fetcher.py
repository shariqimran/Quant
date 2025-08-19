import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta

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

def get_data_summary(df):
    """Get basic data summary statistics"""
    if df is None or df.empty:
        return None
    
    summary = {
        'data_points': len(df),
        'date_range': f"{df['timestamp'].min().date()} to {df['timestamp'].max().date()}",
        'current_price': df['close'].iloc[-1],
        'total_return': ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
    }
    return summary
