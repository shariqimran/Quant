import streamlit as st
import pandas as pd
import numpy as np

# Import our modular components
from src.ui.components import (
    setup_page_config, 
    load_custom_css, 
    render_header, 
    render_sidebar_inputs, 
    render_data_summary, 
    render_welcome_message,
    render_ma_backtest_ui,
    render_volatility_analysis_ui,
    render_rsi_backtest_ui
)
from src.data.data_fetcher import fetch_data, calculate_returns, get_data_summary
from src.indicators.technical_indicators import (
    calculate_moving_averages,
    calculate_volatility,
    calculate_rsi,
    get_moving_average_signals,
    get_rsi_signals,
    get_volatility_summary_stats,
    get_return_statistics
)
from src.visualization.charts import (
    plot_price_with_ma,
    plot_volatility,
    plot_volatility_regimes,
    plot_rsi,
    plot_volatility_distribution
)
from src.strategies.backtest import moving_average_backtest, rsi_backtest
from src.utils.helpers import suppress_warnings

# Suppress warnings
suppress_warnings()

def main():
    """Main application function"""
    # Setup page configuration and styling
    setup_page_config()
    load_custom_css()
    
    # Render header
    render_header()
    
    # Get user inputs from sidebar
    inputs = render_sidebar_inputs()
    
    # Main content area
    if 'fetch_data' in st.session_state and st.session_state.fetch_data:
        with st.spinner("Fetching data..."):
            df = fetch_data(
                inputs['symbol'], 
                inputs['interval'], 
                inputs['start_date'], 
                inputs['end_date']
            )
        
        if df is not None:
            # Calculate all indicators
            df = calculate_returns(df)
            
            # Display basic info
            render_data_summary(df)
            
            # Create tabs for different analyses
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Volatility Analysis", 
                "🔄 RSI Backtest",
                "🧪 MA Backtest",
                "📋 Summary Statistics",
                "📁 Data Export"
            ])
            

            
            # Tab 1: Volatility Analysis
            with tab1:
                # Get volatility parameters from UI
                vol_inputs = render_volatility_analysis_ui()
                
                # Calculate volatility for this analysis
                df_vol = df.copy()
                df_vol = calculate_volatility(df_vol, vol_inputs['fast_vol_window'], vol_inputs['return_type'], inputs['interval'])
                df_vol = calculate_volatility(df_vol, vol_inputs['slow_vol_window'], vol_inputs['return_type'], inputs['interval'])
                
                # Volatility chart
                fig = plot_volatility(df_vol, inputs['symbol'], vol_inputs['fast_vol_window'], vol_inputs['slow_vol_window'], vol_inputs['return_type'])
                st.plotly_chart(fig, use_container_width=True)
                
                # Volatility regimes
                st.subheader("Volatility Regimes")
                fig = plot_volatility_regimes(df_vol, inputs['symbol'], vol_inputs['fast_vol_window'], vol_inputs['slow_vol_window'])
                st.plotly_chart(fig, use_container_width=True)
                
                # Volatility distribution
                st.subheader("Volatility Distribution")
                fig = plot_volatility_distribution(df_vol, vol_inputs['fast_vol_window'], vol_inputs['slow_vol_window'], inputs['symbol'])
                st.plotly_chart(fig, use_container_width=True)
            
            # Tab 2: RSI Backtest
            with tab2:
                rsi_inputs = render_rsi_backtest_ui(inputs['symbol'], inputs['start_date'], inputs['end_date'])
                
                if st.button("Run RSI Backtest", key="run_rsi_backtest"):
                    with st.spinner("Running RSI backtest..."):
                        # Filter df for the selected backtest symbol and date range
                        df_bt = df.copy()
                        if rsi_inputs['backtest_symbol'] and rsi_inputs['backtest_symbol'] != inputs['symbol']:
                            st.warning("Backtest symbol must match loaded data. Please fetch data for the desired symbol first.")
                            final_value, log_df, fig = None, None, None
                        else:
                            # Calculate RSI for backtest
                            df_bt = calculate_rsi(df_bt, rsi_inputs['rsi_period'])
                            
                            # Ensure timestamp and comparison dates are both UTC (timezone-aware)
                            df_bt['timestamp'] = pd.to_datetime(df_bt['timestamp'], utc=True, errors='coerce')
                            start_dt = pd.to_datetime(rsi_inputs['backtest_start'])
                            end_dt = pd.to_datetime(rsi_inputs['backtest_end'])
                            if start_dt.tzinfo is None:
                                start_dt = start_dt.tz_localize('UTC')
                            else:
                                start_dt = start_dt.tz_convert('UTC')
                            if end_dt.tzinfo is None:
                                end_dt = end_dt.tz_localize('UTC')
                            else:
                                end_dt = end_dt.tz_convert('UTC')
                            mask = (df_bt['timestamp'] >= start_dt) & (df_bt['timestamp'] <= end_dt)
                            df_bt = df_bt.loc[mask].reset_index(drop=True)
                            final_value, log_df, fig = rsi_backtest(
                                df_bt, 
                                initial_capital=rsi_inputs['initial_capital'], 
                                symbol=inputs['symbol'],
                                rsi_period=rsi_inputs['rsi_period'],
                                oversold_threshold=rsi_inputs['oversold_threshold'],
                                overbought_threshold=rsi_inputs['overbought_threshold']
                            )
                    
                    if final_value is None:
                        st.error("RSI backtest failed. Not enough data or invalid symbol/date range.")
                    else:
                        st.success(f"Final Portfolio Value: ${final_value:,.2f}")
                        st.plotly_chart(fig, use_container_width=True)
                        st.subheader("Trade Log")
                        st.dataframe(log_df)
            
            # Tab 4: Summary Statistics
            with tab4:
                st.subheader("Summary Statistics")
                
                # Get volatility parameters (using default values for summary)
                fast_vol_window = 20
                slow_vol_window = 60
                return_type = "log"  # Default to log returns for summary
                
                # Calculate volatility for summary
                df_summary = df.copy()
                df_summary = calculate_volatility(df_summary, fast_vol_window, return_type, inputs['interval'])
                df_summary = calculate_volatility(df_summary, slow_vol_window, return_type, inputs['interval'])
                
                # Volatility summary
                vol_stats = get_volatility_summary_stats(df_summary, fast_vol_window, slow_vol_window)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**📊 Volatility Summary (Annualized)**")
                    st.metric("Fast Vol Mean", f"{vol_stats['fast_mean']:.3f}")
                    st.metric("Fast Vol Median", f"{vol_stats['fast_median']:.3f}")
                    st.metric("Fast Vol 95th Percentile", f"{vol_stats['fast_95p']:.3f}")
                    st.metric("Slow Vol Mean", f"{vol_stats['slow_mean']:.3f}")
                    st.metric("Slow Vol Median", f"{vol_stats['slow_median']:.3f}")
                    st.metric("Slow Vol 95th Percentile", f"{vol_stats['slow_95p']:.3f}")
                
                with col2:
                    st.markdown("**📈 Regime Coverage**")
                    st.metric("Low Vol Regime (<25%)", f"{vol_stats['share_low']*100:.1f}%")
                    st.metric("Normal Regime", f"{vol_stats['share_mid']*100:.1f}%")
                    st.metric("High Vol Regime (>75%)", f"{vol_stats['share_high']*100:.1f}%")
                    st.metric("Low Vol Threshold", f"{vol_stats['low_threshold']:.3f}")
                    st.metric("High Vol Threshold", f"{vol_stats['high_threshold']:.3f}")
                
                # Return statistics
                st.subheader("Return Statistics")
                return_stats = get_return_statistics(df)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mean Return", f"{return_stats['mean_return']:.4f}%")
                with col2:
                    st.metric("Volatility", f"{return_stats['volatility']:.4f}%")
                with col3:
                    st.metric("Sharpe Ratio", f"{return_stats['sharpe_ratio']:.3f}")
                with col4:
                    st.metric("Max Drawdown", f"{return_stats['max_drawdown']:.2f}%")
            
            # Tab 5: Data Export
            with tab5:
                st.subheader("Data Export")
                
                # Download processed data
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Processed Data (CSV)",
                    data=csv,
                    file_name=f"{inputs['symbol']}_{inputs['interval']}_{inputs['start_date']}_{inputs['end_date']}_processed.csv",
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
            
            # Tab 3: MA Backtest
            with tab3:
                backtest_inputs = render_ma_backtest_ui(inputs['symbol'], inputs['start_date'], inputs['end_date'])
                
                if st.button("Run MA Backtest", key="run_ma_backtest"):
                    with st.spinner("Running backtest..."):
                        # Filter df for the selected backtest symbol and date range
                        df_bt = df.copy()
                        if backtest_inputs['backtest_symbol'] != inputs['symbol']:
                            st.warning("Backtest symbol must match loaded data. Please fetch data for the desired symbol first.")
                            final_value, log_df, fig = None, None, None
                        else:
                            # Calculate moving averages for backtest
                            df_bt = calculate_moving_averages(df_bt, backtest_inputs['short_window'], backtest_inputs['long_window'])
                            
                            # Ensure timestamp and comparison dates are both UTC (timezone-aware)
                            df_bt['timestamp'] = pd.to_datetime(df_bt['timestamp'], utc=True, errors='coerce')
                            start_dt = pd.to_datetime(backtest_inputs['backtest_start'])
                            end_dt = pd.to_datetime(backtest_inputs['backtest_end'])
                            if start_dt.tzinfo is None:
                                start_dt = start_dt.tz_localize('UTC')
                            else:
                                start_dt = start_dt.tz_convert('UTC')
                            if end_dt.tzinfo is None:
                                end_dt = end_dt.tz_localize('UTC')
                            else:
                                end_dt = end_dt.tz_convert('UTC')
                            mask = (df_bt['timestamp'] >= start_dt) & (df_bt['timestamp'] <= end_dt)
                            df_bt = df_bt.loc[mask].reset_index(drop=True)
                            final_value, log_df, fig = moving_average_backtest(
                                df_bt, 
                                initial_capital=backtest_inputs['initial_capital'], 
                                symbol=backtest_inputs['backtest_symbol']
                            )
                    
                    if final_value is None:
                        st.error("Backtest failed. Not enough data or invalid symbol/date range.")
                    else:
                        st.success(f"Final Portfolio Value: ${final_value:,.2f}")
                        st.plotly_chart(fig, use_container_width=True)
                        st.subheader("Trade Log")
                        st.dataframe(log_df)
        
        else:
            st.error("Failed to fetch data. Please check your symbol and try again.")
    
    else:
        # Welcome message
        render_welcome_message()

if __name__ == "__main__":
    main()
