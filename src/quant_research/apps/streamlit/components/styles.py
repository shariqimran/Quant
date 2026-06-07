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
        .stApp {
            background:
                radial-gradient(circle at 78% 12%, rgba(47, 255, 178, 0.10), transparent 34rem),
                radial-gradient(circle at 18% 38%, rgba(81, 215, 255, 0.09), transparent 30rem),
                linear-gradient(135deg, #030711 0%, #07101f 48%, #02040b 100%);
        }
        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(148, 163, 184, 0.18);
            background: rgba(4, 11, 22, 0.92);
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
        .qa-landing-hero {
            min-height: 620px;
            display: grid;
            grid-template-columns: minmax(0, 0.92fr) minmax(420px, 1.08fr);
            gap: clamp(2rem, 5vw, 4.8rem);
            align-items: center;
            padding: clamp(1.8rem, 5vw, 4.5rem) 0 clamp(2rem, 5vw, 4rem);
            position: relative;
        }
        .qa-landing-hero:before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            background-image:
                linear-gradient(rgba(123, 157, 189, 0.07) 1px, transparent 1px),
                linear-gradient(90deg, rgba(123, 157, 189, 0.07) 1px, transparent 1px);
            background-size: 64px 64px;
            mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.95), transparent 86%);
        }
        .qa-hero-copy,
        .qa-dashboard-preview {
            position: relative;
            z-index: 1;
        }
        .qa-eyebrow,
        .qa-section-kicker {
            display: inline-flex;
            align-items: center;
            gap: 0.6rem;
            color: #2fffb2;
            text-transform: uppercase;
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.08rem;
            margin-bottom: 0.85rem;
        }
        .qa-eyebrow span {
            width: 0.5rem;
            height: 0.5rem;
            border-radius: 999px;
            background: #2fffb2;
            box-shadow: 0 0 0 0 rgba(47, 255, 178, 0.55);
            animation: qa-pulse 1.8s infinite;
        }
        .qa-landing-hero h1 {
            color: #eef7ff;
            font-size: clamp(3rem, 6.4vw, 6.2rem);
            line-height: 0.92;
            letter-spacing: 0;
            margin: 0 0 1.25rem;
        }
        .qa-landing-hero p,
        .qa-story-panel p,
        .qa-feature-grid p,
        .qa-workflow h2 {
            color: #9eb2c7;
            line-height: 1.68;
        }
        .qa-landing-hero p {
            font-size: 1.06rem;
            max-width: 42rem;
            margin-bottom: 1.55rem;
        }
        .qa-hero-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.8rem;
            margin-bottom: 1.65rem;
        }
        .qa-button {
            min-height: 3rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            padding: 0 1.1rem;
            font-weight: 800;
            text-decoration: none !important;
            transition: transform 180ms ease, border-color 180ms ease, background 180ms ease;
        }
        .qa-button:hover {
            transform: translateY(-2px);
        }
        .qa-button-primary {
            color: #03120c !important;
            background: linear-gradient(135deg, #2fffb2, #51d7ff);
            box-shadow: 0 16px 42px rgba(47, 255, 178, 0.18);
        }
        .qa-button-secondary {
            color: #d3e2ef !important;
            border: 1px solid rgba(154, 184, 210, 0.18);
            background: rgba(255, 255, 255, 0.05);
        }
        .qa-hero-stats,
        .qa-mini-grid,
        .qa-feature-grid {
            display: grid;
            gap: 0.8rem;
        }
        .qa-hero-stats {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
        .qa-hero-stats div,
        .qa-mini-grid div,
        .qa-feature-grid article,
        .qa-story-panel,
        .qa-workflow {
            border: 1px solid rgba(154, 184, 210, 0.18);
            border-radius: 8px;
            background: rgba(10, 22, 38, 0.72);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
        }
        .qa-hero-stats div {
            padding: 0.9rem;
        }
        .qa-hero-stats strong,
        .qa-hero-stats span {
            display: block;
        }
        .qa-hero-stats strong {
            color: #eef7ff;
            font-size: 0.78rem;
            text-transform: uppercase;
        }
        .qa-hero-stats span {
            color: #9eb2c7;
            margin-top: 0.3rem;
            font-size: 0.82rem;
        }
        .qa-dashboard-preview {
            border: 1px solid rgba(154, 184, 210, 0.22);
            border-radius: 8px;
            overflow: hidden;
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.08), transparent 24%),
                rgba(7, 17, 31, 0.76);
            box-shadow: 0 28px 90px rgba(0, 0, 0, 0.46), inset 0 1px 0 rgba(255, 255, 255, 0.09);
            transform: rotateX(4deg) rotateY(-7deg);
            animation: qa-float 6s ease-in-out infinite;
        }
        .qa-window-bar,
        .qa-ticker-row,
        .qa-panel-heading {
            display: flex;
            align-items: center;
        }
        .qa-window-bar {
            height: 3rem;
            padding: 0 1rem;
            gap: 0.5rem;
            border-bottom: 1px solid rgba(154, 184, 210, 0.18);
            color: #7890a8;
            font-family: "Source Code Pro", monospace;
            font-size: 0.72rem;
        }
        .qa-window-bar i {
            width: 0.62rem;
            height: 0.62rem;
            border-radius: 999px;
            background: #54667c;
        }
        .qa-window-bar i:nth-child(1) { background: #ff6f91; }
        .qa-window-bar i:nth-child(2) { background: #ffcf5a; }
        .qa-window-bar i:nth-child(3) { background: #2fffb2; }
        .qa-window-bar span {
            margin-left: auto;
        }
        .qa-ticker-row {
            gap: 0.6rem;
            flex-wrap: wrap;
            padding: 1rem 1.1rem 0.25rem;
        }
        .qa-ticker-row span {
            border: 1px solid rgba(154, 184, 210, 0.18);
            border-radius: 8px;
            padding: 0.48rem 0.62rem;
            background: rgba(255, 255, 255, 0.045);
            color: #d3e2ef;
            font-family: "Source Code Pro", monospace;
            font-size: 0.72rem;
        }
        .qa-chart-panel {
            margin: 0.85rem 1.1rem 0.75rem;
            padding: 1rem 1rem 0.35rem;
            border: 1px solid rgba(154, 184, 210, 0.18);
            border-radius: 8px;
            background: linear-gradient(180deg, rgba(81, 215, 255, 0.055), transparent), rgba(4, 10, 18, 0.46);
        }
        .qa-panel-heading {
            justify-content: space-between;
            margin-bottom: 0.35rem;
        }
        .qa-panel-heading span,
        .qa-mini-grid span {
            color: #9eb2c7;
            font-size: 0.76rem;
            font-weight: 800;
            text-transform: uppercase;
        }
        .qa-panel-heading strong,
        .qa-mini-grid strong {
            color: #2fffb2;
            font-family: "Source Code Pro", monospace;
        }
        .qa-equity-chart {
            width: 100%;
            min-height: 15rem;
        }
        .qa-grid path {
            fill: none;
            stroke: rgba(154, 184, 210, 0.15);
            stroke-width: 1;
        }
        .qa-chart-fill {
            fill: url("#qa-fill");
        }
        .qa-chart-line {
            fill: none;
            stroke: url("#qa-line");
            stroke-width: 5;
            stroke-linecap: round;
            filter: drop-shadow(0 0 13px rgba(47, 255, 178, 0.55));
            stroke-dasharray: 1;
            stroke-dashoffset: 1;
            animation: qa-draw-line 2.2s ease forwards 350ms;
        }
        .qa-mini-grid {
            grid-template-columns: repeat(3, minmax(0, 1fr));
            padding: 0 1.1rem 1.1rem;
        }
        .qa-mini-grid div {
            padding: 0.9rem;
        }
        .qa-mini-grid strong,
        .qa-mini-grid small {
            display: block;
        }
        .qa-mini-grid strong {
            margin-top: 0.35rem;
            font-size: 1.28rem;
        }
        .qa-mini-grid small {
            margin-top: 0.25rem;
            color: #8096ac;
        }
        .qa-story-panel {
            display: grid;
            grid-template-columns: minmax(0, 0.82fr) minmax(320px, 1fr);
            gap: clamp(1.5rem, 4vw, 4rem);
            padding: clamp(1.4rem, 4vw, 2.2rem);
            margin-bottom: 3rem;
        }
        .qa-story-panel h2,
        .qa-feature-section h2 {
            color: #eef7ff;
            font-size: clamp(2rem, 4vw, 4.1rem);
            line-height: 1;
            margin: 0;
        }
        .qa-story-panel p {
            margin: 0;
            font-size: 1rem;
        }
        .qa-feature-section {
            margin-bottom: 3rem;
        }
        .qa-feature-section h2 {
            max-width: 44rem;
            margin-bottom: 1.45rem;
        }
        .qa-feature-grid {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
        .qa-feature-grid article {
            min-height: 12.5rem;
            padding: 1.25rem;
            position: relative;
            overflow: hidden;
            transition: transform 180ms ease, border-color 180ms ease;
        }
        .qa-feature-grid article:hover {
            transform: translateY(-5px);
            border-color: rgba(81, 215, 255, 0.42);
        }
        .qa-feature-grid article:after {
            content: "";
            position: absolute;
            left: 1.25rem;
            right: 1.25rem;
            bottom: 0;
            height: 2px;
            background: linear-gradient(90deg, #51d7ff, #2fffb2, #ffcf5a);
        }
        .qa-feature-grid span {
            display: block;
            color: #2fffb2;
            font-family: "Source Code Pro", monospace;
            font-size: 0.82rem;
            margin-bottom: 2.3rem;
        }
        .qa-feature-grid h3 {
            color: #eef7ff;
            font-size: 1.04rem;
            margin: 0 0 0.55rem;
        }
        .qa-feature-grid p {
            margin: 0;
            font-size: 0.9rem;
        }
        .qa-workflow {
            padding: clamp(1.35rem, 4vw, 2rem);
            margin-bottom: 2.2rem;
        }
        .qa-workflow h2 {
            color: #eef7ff;
            font-size: clamp(1.4rem, 3vw, 2.25rem);
            line-height: 1.18;
            margin: 0;
            max-width: 60rem;
        }
        @keyframes qa-pulse {
            0% { box-shadow: 0 0 0 0 rgba(47, 255, 178, 0.55); }
            70% { box-shadow: 0 0 0 12px rgba(47, 255, 178, 0); }
            100% { box-shadow: 0 0 0 0 rgba(47, 255, 178, 0); }
        }
        @keyframes qa-float {
            0%, 100% { transform: rotateX(4deg) rotateY(-7deg) translateY(0); }
            50% { transform: rotateX(3deg) rotateY(-5deg) translateY(-10px); }
        }
        @keyframes qa-draw-line {
            to { stroke-dashoffset: 0; }
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
        @media (max-width: 980px) {
            .qa-landing-hero,
            .qa-story-panel {
                grid-template-columns: 1fr;
            }
            .qa-dashboard-preview {
                transform: none;
                animation: none;
            }
            .qa-feature-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        @media (max-width: 680px) {
            .qa-hero-stats,
            .qa-mini-grid,
            .qa-feature-grid {
                grid-template-columns: 1fr;
            }
            .qa-landing-hero {
                min-height: auto;
            }
            .qa-landing-hero h1 {
                font-size: 3rem;
            }
        }
        @media (prefers-reduced-motion: reduce) {
            .qa-eyebrow span,
            .qa-dashboard-preview,
            .qa-chart-line {
                animation: none;
            }
            .qa-chart-line {
                stroke-dashoffset: 0;
            }
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
