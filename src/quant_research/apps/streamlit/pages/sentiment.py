"""Sentiment analysis page."""

import streamlit as st

from src.quant_research.apps.streamlit.components.forms import render_sentiment_analysis_ui
from src.quant_research.sentiment.analyzer import analyze_symbol


def render_sentiment_page(inputs):
    """Render sentiment analysis page."""
    should_analyze = render_sentiment_analysis_ui(inputs["symbol"])

    if should_analyze:
        with st.spinner("Fetching and analyzing sentiment data..."):
            try:
                sentiment_result = analyze_symbol(inputs["symbol"])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Verdict", sentiment_result["verdict"])
                with col2:
                    st.metric("Confidence", f"{sentiment_result['confidence']:.2f}")
                with col3:
                    st.metric("Volume", sentiment_result["metrics"].get("V", 0))

                st.subheader("Sentiment Metrics")
                metrics = sentiment_result["metrics"]
                if metrics:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Sentiment Score", f"{metrics.get('S', 0):.3f}")
                    with col2:
                        st.metric("Breadth", f"{metrics.get('breadth', 0):.3f}")
                    with col3:
                        st.metric("Intensity", f"{metrics.get('intensity', 0):.3f}")
                    with col4:
                        st.metric("Volume", metrics.get("V", 0))

                if sentiment_result["reasons"]:
                    st.subheader("Top Sentiment Sources")
                    for i, reason in enumerate(sentiment_result["reasons"], 1):
                        with st.expander(f"Source {i}: {reason['src']} (Score: {reason['score']:.3f})"):
                            st.write(f"**Excerpt:** {reason['excerpt']}")
                            st.write(f"**Link:** [{reason['link']}]({reason['link']})")

            except Exception as e:
                st.error(f"Error analyzing sentiment: {str(e)}")
                st.info("This might be due to network issues or rate limiting. Please try again later.")
