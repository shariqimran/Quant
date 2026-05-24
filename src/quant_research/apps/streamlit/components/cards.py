"""Reusable dashboard card components."""

import streamlit as st


def format_money(value):
    """Format a number as a US-dollar string."""
    return f"${value:,.2f}"


def render_kpi_card(label, value, note="", note_class=""):
    """Render a custom KPI card."""
    note_markup = f'<div class="kpi-note {note_class}">{note}</div>' if note else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <p class="kpi-value">{value}</p>
            {note_markup}
        </div>
        """,
        unsafe_allow_html=True,
    )

