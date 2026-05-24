"""Streamlit page configuration and custom CSS."""

import streamlit as st


def setup_page_config():
    """Configure Streamlit page metadata and layout."""
    st.set_page_config(
        page_title="Quant Research Workbench",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def load_custom_css():
    """Load dashboard CSS."""
    st.markdown(
        """
    <style>
        header[data-testid="stHeader"] {
            background: transparent;
        }
        footer {
            visibility: hidden;
        }
        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }
        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(148, 163, 184, 0.18);
            background: #111827;
        }
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.75rem;
        }
        section[data-testid="stSidebar"] h1 {
            font-size: 1.3rem;
            letter-spacing: 0;
            margin-bottom: 0.35rem;
            color: #f8fafc;
        }
        .main-header {
            font-size: 1.58rem;
            font-weight: 750;
            color: #f8fafc;
            margin-bottom: 0.05rem;
            letter-spacing: 0;
        }
        .app-subtitle {
            color: #94a3b8;
            font-size: 0.92rem;
            margin-bottom: 1.25rem;
        }
        .hero-panel {
            border: 1px solid rgba(56, 189, 248, 0.18);
            border-radius: 12px;
            padding: 1.25rem 1.35rem;
            background:
                linear-gradient(135deg, rgba(14, 165, 233, 0.16), rgba(15, 23, 42, 0.78)),
                #111827;
            margin-bottom: 1rem;
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.18);
        }
        .hero-kicker {
            color: #38bdf8;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.04rem;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }
        .hero-title {
            color: #f8fafc;
            font-size: 1.9rem;
            font-weight: 760;
            margin: 0;
            letter-spacing: 0;
            line-height: 1.15;
        }
        .hero-subtitle {
            color: #cbd5e1;
            font-size: 0.95rem;
            margin-top: 0.55rem;
            max-width: 780px;
        }
        .kpi-card {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 10px;
            padding: 0.9rem 1rem;
            background: #111827;
            min-height: 96px;
        }
        .kpi-label {
            color: #94a3b8;
            font-size: 0.76rem;
            font-weight: 650;
            text-transform: uppercase;
            letter-spacing: 0.03rem;
            margin-bottom: 0.45rem;
        }
        .kpi-value {
            color: #f8fafc;
            font-size: 1.45rem;
            font-weight: 760;
            line-height: 1.1;
            margin: 0;
        }
        .kpi-note {
            color: #94a3b8;
            font-size: 0.82rem;
            margin-top: 0.35rem;
        }
        .delta-positive {
            color: #22c55e;
        }
        .delta-negative {
            color: #f87171;
        }
        .empty-state {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 10px;
            padding: 1.35rem;
            background: #111827;
            color: #f8fafc;
            margin-bottom: 1rem;
        }
        .empty-state p {
            color: #94a3b8;
        }
        .dashboard-card {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 10px;
            padding: 1rem 1rem 0.95rem 1rem;
            background: #111827;
            min-height: 132px;
            position: relative;
            overflow: hidden;
        }
        .dashboard-card:before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 3px;
            background: #38bdf8;
            opacity: 0.9;
        }
        .dashboard-card h4 {
            margin: 0 0 0.5rem 0;
            font-size: 1rem;
            color: #f8fafc;
        }
        .dashboard-card p {
            margin: 0;
            color: #94a3b8;
            font-size: 0.88rem;
            line-height: 1.38;
        }
        .module-tag {
            display: inline-block;
            margin-top: 0.85rem;
            font-size: 0.74rem;
            color: #38bdf8;
            font-weight: 700;
        }
        .section-label {
            color: #94a3b8;
            font-size: 0.78rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.04rem;
            margin: 1.1rem 0 0.55rem 0;
        }
        .status-pill {
            display: inline-flex;
            align-items: center;
            border: 1px solid rgba(56, 189, 248, 0.30);
            border-radius: 999px;
            padding: 0.22rem 0.58rem;
            font-size: 0.78rem;
            color: #bae6fd;
            background: rgba(14, 165, 233, 0.12);
        }
        .workflow-strip {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 10px;
            padding: 0.75rem 0.85rem;
            background: #111827;
            margin-top: 0.5rem;
        }
        .workflow-step {
            color: #e5e7eb;
            font-size: 0.88rem;
            margin: 0.32rem 0;
        }
        .workflow-index {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.35rem;
            height: 1.35rem;
            border-radius: 999px;
            background: rgba(14, 165, 233, 0.18);
            color: #7dd3fc;
            font-size: 0.72rem;
            font-weight: 750;
            margin-right: 0.45rem;
        }
        div[data-testid="stMetric"] {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 8px;
            padding: 0.75rem 0.85rem;
            background: #111827;
        }
        button[kind="primary"] {
            border-radius: 7px;
            font-weight: 650;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 46px;
            white-space: pre-wrap;
            background-color: #111827;
            color: #e5e7eb;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 8px;
            padding-bottom: 8px;
        }
        .stTabs [aria-selected="true"] {
            border-bottom: 2px solid #38bdf8;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

