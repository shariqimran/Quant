"""Data export page."""

import streamlit as st


def render_export_page(df, inputs):
    """Render export page."""
    st.subheader("Export")
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download processed data",
        data=csv,
        file_name=f"{inputs['symbol']}_{inputs['interval']}_{inputs['start_date']}_{inputs['end_date']}_processed.csv",
        mime="text/csv",
    )

    st.markdown("#### Preview")
    st.dataframe(df.head(20), use_container_width=True)

    st.markdown("#### Data information")
    st.write(f"**Shape:** {df.shape}")
    st.write(f"**Columns:** {list(df.columns)}")
    st.write("**Missing Values:**")
    st.write(df.isna().sum())
