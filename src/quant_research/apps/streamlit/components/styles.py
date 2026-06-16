"""Streamlit page configuration and custom CSS."""

import streamlit as st


THEME_VARS = {
    "dark": {
        "color-scheme": "dark",
        "--qa-bg": "#040816",
        "--qa-bg-elevated": "rgba(7, 13, 28, 0.94)",
        "--qa-bg-subtle": "rgba(16, 24, 44, 0.72)",
        "--qa-bg-soft": "rgba(255, 255, 255, 0.05)",
        "--qa-surface": "rgba(10, 19, 36, 0.84)",
        "--qa-surface-strong": "#0f172a",
        "--qa-surface-accent": "rgba(70, 194, 255, 0.12)",
        "--qa-border": "rgba(148, 163, 184, 0.20)",
        "--qa-border-strong": "rgba(70, 194, 255, 0.36)",
        "--qa-text": "#dbe7f3",
        "--qa-text-strong": "#f8fbff",
        "--qa-text-muted": "#92a6be",
        "--qa-text-soft": "#c9d7e6",
        "--qa-success": "#22c55e",
        "--qa-warning": "#f59e0b",
        "--qa-danger": "#fb7185",
        "--qa-shadow": "0 18px 48px rgba(2, 6, 23, 0.28)",
    },
    "light": {
        "color-scheme": "light",
        "--qa-bg": "#eef4fb",
        "--qa-bg-elevated": "rgba(248, 251, 255, 0.96)",
        "--qa-bg-subtle": "rgba(255, 255, 255, 0.92)",
        "--qa-bg-soft": "rgba(14, 165, 233, 0.07)",
        "--qa-surface": "rgba(255, 255, 255, 0.96)",
        "--qa-surface-strong": "#ffffff",
        "--qa-surface-accent": "rgba(14, 165, 233, 0.08)",
        "--qa-border": "rgba(148, 163, 184, 0.24)",
        "--qa-border-strong": "rgba(2, 132, 199, 0.28)",
        "--qa-text": "#162235",
        "--qa-text-strong": "#081121",
        "--qa-text-muted": "#516277",
        "--qa-text-soft": "#334155",
        "--qa-success": "#15803d",
        "--qa-warning": "#b45309",
        "--qa-danger": "#dc2626",
        "--qa-shadow": "0 14px 32px rgba(15, 23, 42, 0.08)",
    },
}

ACCENT_VARS = {
    "Sky": {
        "--qa-accent": "#46c2ff",
        "--qa-accent-strong": "#0ea5e9",
        "--qa-accent-soft": "rgba(70, 194, 255, 0.16)",
        "--qa-accent-alt": "#2dd4bf",
        "--qa-accent-warm": "#fbbf24",
        "--qa-accent-rose": "#fb7185",
    },
    "Teal": {
        "--qa-accent": "#2dd4bf",
        "--qa-accent-strong": "#0f766e",
        "--qa-accent-soft": "rgba(45, 212, 191, 0.16)",
        "--qa-accent-alt": "#38bdf8",
        "--qa-accent-warm": "#f59e0b",
        "--qa-accent-rose": "#fb7185",
    },
    "Violet": {
        "--qa-accent": "#8b5cf6",
        "--qa-accent-strong": "#7c3aed",
        "--qa-accent-soft": "rgba(139, 92, 246, 0.16)",
        "--qa-accent-alt": "#38bdf8",
        "--qa-accent-warm": "#fbbf24",
        "--qa-accent-rose": "#fb7185",
    },
}


def _css_var_block(selector, variables):
    lines = [f"            {name}: {value};" for name, value in variables.items()]
    return f"        {selector} {{\n" + "\n".join(lines) + "\n        }\n"


def _theme_override_css(theme_mode, accent_mode, motion_enabled):
    css_parts = []

    if theme_mode == "Dark":
        css_parts.append(_css_var_block(":root", THEME_VARS["dark"]))
    elif theme_mode == "Light":
        css_parts.append(_css_var_block(":root", THEME_VARS["light"]))

    accent_vars = ACCENT_VARS.get(accent_mode, ACCENT_VARS["Sky"])
    css_parts.append(_css_var_block(":root", accent_vars))

    if not motion_enabled:
        css_parts.append(
            """
        *, *::before, *::after {
            animation: none !important;
            transition: none !important;
            scroll-behavior: auto !important;
        }
        """
        )

    return "\n".join(css_parts)


def setup_page_config():
    """Configure Streamlit page metadata and layout."""
    st.set_page_config(
        page_title="Quant Research Workbench",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def load_custom_css(theme_mode="System", accent_mode="Sky", motion_enabled=True):
    """Load dashboard CSS."""
    theme_override_css = _theme_override_css(theme_mode, accent_mode, motion_enabled)
    st.markdown(
        """
    <style>
        :root {
            font-size: 14px !important;
            color-scheme: dark;
            --qa-bg: #040816;
            --qa-bg-elevated: rgba(7, 13, 28, 0.94);
            --qa-bg-subtle: rgba(16, 24, 44, 0.72);
            --qa-bg-soft: rgba(255, 255, 255, 0.05);
            --qa-surface: rgba(10, 19, 36, 0.84);
            --qa-surface-strong: #0f172a;
            --qa-surface-accent: rgba(70, 194, 255, 0.12);
            --qa-border: rgba(148, 163, 184, 0.20);
            --qa-border-strong: rgba(70, 194, 255, 0.36);
            --qa-text: #dbe7f3;
            --qa-text-strong: #f8fbff;
            --qa-text-muted: #92a6be;
            --qa-text-soft: #c9d7e6;
            --qa-accent: #46c2ff;
            --qa-accent-strong: #0ea5e9;
            --qa-accent-soft: rgba(70, 194, 255, 0.16);
            --qa-accent-alt: #2dd4bf;
            --qa-accent-warm: #fbbf24;
            --qa-accent-rose: #fb7185;
            --qa-success: #22c55e;
            --qa-warning: #f59e0b;
            --qa-danger: #fb7185;
            --qa-shadow: 0 18px 48px rgba(2, 6, 23, 0.28);
        }
        @media (prefers-color-scheme: light) {
            :root {
                color-scheme: light;
                --qa-bg: #eef4fb;
                --qa-bg-elevated: rgba(248, 251, 255, 0.96);
                --qa-bg-subtle: rgba(255, 255, 255, 0.92);
                --qa-bg-soft: rgba(14, 165, 233, 0.07);
                --qa-surface: rgba(255, 255, 255, 0.96);
                --qa-surface-strong: #ffffff;
                --qa-surface-accent: rgba(14, 165, 233, 0.08);
                --qa-border: rgba(148, 163, 184, 0.24);
                --qa-border-strong: rgba(2, 132, 199, 0.28);
                --qa-text: #162235;
                --qa-text-strong: #081121;
                --qa-text-muted: #516277;
                --qa-text-soft: #334155;
                --qa-accent: #0284c7;
                --qa-accent-strong: #0369a1;
                --qa-accent-soft: rgba(2, 132, 199, 0.10);
                --qa-accent-alt: #0f766e;
                --qa-accent-warm: #d97706;
                --qa-accent-rose: #e11d48;
                --qa-success: #15803d;
                --qa-warning: #b45309;
                --qa-danger: #dc2626;
                --qa-shadow: 0 14px 32px rgba(15, 23, 42, 0.08);
            }
        }
"""
        + theme_override_css
        + """
        html,
        body,
        [data-testid="stAppViewContainer"],
        .stApp,
        button,
        input,
        textarea,
        select {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
        }
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
            width: min(1180px, calc(100vw - 3rem));
        }
        .stApp {
            color: var(--qa-text);
            background:
                radial-gradient(circle at 78% 12%, color-mix(in srgb, var(--qa-accent-alt) 18%, transparent), transparent 34rem),
                radial-gradient(circle at 18% 38%, color-mix(in srgb, var(--qa-accent) 20%, transparent), transparent 30rem),
                radial-gradient(circle at 58% 82%, color-mix(in srgb, var(--qa-accent-rose) 10%, transparent), transparent 28rem),
                linear-gradient(135deg, var(--qa-bg) 0%, color-mix(in srgb, var(--qa-bg) 88%, #0f172a 12%) 48%, var(--qa-bg) 100%);
            animation: qa-background-drift 18s ease-in-out infinite alternate;
        }
        .stMarkdown,
        .stMarkdown p,
        .stCaption,
        label,
        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {
            overflow-wrap: anywhere;
            word-break: normal;
        }
        .stMarkdown p,
        .stCaption,
        label,
        div[data-testid="stMetricLabel"] p,
        div[data-testid="stMetricValue"] p,
        div[data-testid="stMetricDelta"] p,
        .stSelectbox label,
        .stTextInput label,
        .stNumberInput label,
        .stDateInput label,
        .stCheckbox label,
        .stRadio label {
            font-size: 0.92rem !important;
        }
        h1, .stMarkdown h1 {
            font-size: clamp(1.8rem, 1.2rem + 2vw, 2.7rem) !important;
            line-height: 1.1 !important;
        }
        h2, .stMarkdown h2 {
            font-size: clamp(1.35rem, 1rem + 1.4vw, 1.95rem) !important;
            line-height: 1.15 !important;
        }
        h3, .stMarkdown h3 {
            font-size: clamp(1.1rem, 0.95rem + 0.8vw, 1.4rem) !important;
            line-height: 1.2 !important;
        }
        h4, .stMarkdown h4 {
            font-size: 1rem !important;
            line-height: 1.25 !important;
        }
        .stMarkdown p,
        .stCaption,
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricDelta"],
        [data-testid="stDataFrame"] table,
        [data-testid="stDataFrame"] div {
            min-width: 0;
        }
        div[data-testid="stMetricLabel"] p,
        div[data-testid="stMetricValue"] p,
        div[data-testid="stMetricDelta"] p {
            overflow-wrap: anywhere;
            word-break: break-word;
            line-height: 1.2;
        }
        div[data-testid="stMetricValue"] {
            max-width: 100%;
        }
        div[data-testid="stMetricValue"] > div,
        div[data-testid="stMetricLabel"] > div {
            width: 100%;
        }
        [data-testid="column"] {
            min-width: 0;
        }
        [data-testid="column"] .stMarkdown,
        [data-testid="column"] .stCaption,
        [data-testid="column"] div[data-testid="stMetric"] {
            min-width: 0;
        }
        section[data-testid="stSidebar"] {
            border-right: 1px solid var(--qa-border);
            background: var(--qa-bg-elevated);
        }
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.75rem;
        }
        section[data-testid="stSidebar"] h1 {
            font-size: 1.3rem;
            letter-spacing: 0;
            margin-bottom: 0.35rem;
            color: var(--qa-text-strong);
        }
        section[data-testid="stSidebar"] .stCaption {
            color: var(--qa-accent);
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.08rem;
            font-weight: 700;
        }
        section[data-testid="stSidebar"] button[kind="secondary"],
        section[data-testid="stSidebar"] button[kind="primary"] {
            min-height: 2.65rem;
            justify-content: flex-start;
            border-radius: 10px;
            font-size: 0.92rem;
            font-weight: 600;
            box-shadow: none;
            transition: background 180ms ease, color 180ms ease, transform 180ms ease, border-color 180ms ease;
        }
        section[data-testid="stSidebar"] button[kind="secondary"] p,
        section[data-testid="stSidebar"] button[kind="primary"] p,
        section[data-testid="stSidebar"] button[kind="secondary"] span,
        section[data-testid="stSidebar"] button[kind="primary"] span,
        section[data-testid="stSidebar"] button[kind="secondary"] div,
        section[data-testid="stSidebar"] button[kind="primary"] div {
            transition: color 180ms ease;
        }
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background: transparent;
            border: 1px solid transparent;
            color: var(--qa-text-muted);
        }
        section[data-testid="stSidebar"] button[kind="secondary"]:hover,
        section[data-testid="stSidebar"] button[kind="secondary"]:focus-visible {
            background: var(--qa-bg-soft);
            border-color: transparent;
        }
        section[data-testid="stSidebar"] button[kind="primary"] {
            background: color-mix(in srgb, var(--qa-accent) 12%, var(--qa-surface-strong) 88%) !important;
            border: 1px solid var(--qa-border-strong) !important;
            color: var(--qa-text-strong) !important;
            box-shadow: 0 8px 18px color-mix(in srgb, var(--qa-accent) 10%, transparent) !important;
        }
        section[data-testid="stSidebar"] button[kind="primary"]:hover,
        section[data-testid="stSidebar"] button[kind="primary"]:focus-visible {
            background: color-mix(in srgb, var(--qa-accent) 18%, var(--qa-surface-strong) 82%) !important;
            border-color: color-mix(in srgb, var(--qa-accent) 72%, white 28%) !important;
            transform: translateY(-1px);
        }
        section[data-testid="stSidebar"] button[kind="secondary"] > div,
        section[data-testid="stSidebar"] button[kind="primary"] > div,
        section[data-testid="stSidebar"] button[kind="secondary"] span,
        section[data-testid="stSidebar"] button[kind="primary"] span {
            width: auto;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            text-align: left;
        }
        section[data-testid="stSidebar"] button[kind="primary"] > div,
        section[data-testid="stSidebar"] button[kind="primary"] span {
            color: var(--qa-text-strong) !important;
        }
        .main-header {
            font-size: clamp(1.7rem, 1.2rem + 1.6vw, 2.5rem);
            font-weight: 780;
            color: var(--qa-text-strong);
            margin: 0;
            letter-spacing: 0;
            line-height: 1.02;
        }
        .app-subtitle {
            color: var(--qa-text-muted);
            font-size: clamp(0.9rem, 0.84rem + 0.24vw, 0.98rem);
            margin: 0.55rem 0 0;
            line-height: 1.5;
            max-width: 48rem;
        }
        .brand-header {
            margin-bottom: 1.4rem;
        }
        .brand-mark {
            display: inline-flex;
            align-items: center;
            gap: 0.7rem;
            margin-bottom: 0.7rem;
        }
        .brand-dot {
            width: 0.7rem;
            height: 0.7rem;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--qa-accent-alt), var(--qa-accent));
            box-shadow: 0 0 0 6px color-mix(in srgb, var(--qa-accent) 12%, transparent);
        }
        .brand-chip {
            display: inline-flex;
            align-items: center;
            min-height: 1.95rem;
            padding: 0 0.78rem;
            border-radius: 999px;
            border: 1px solid var(--qa-border-strong);
            background: color-mix(in srgb, var(--qa-accent) 8%, var(--qa-surface-strong) 92%);
            color: var(--qa-accent);
            font-size: 0.78rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.05rem;
        }
        .sidebar-brand {
            margin-bottom: 0.9rem;
            padding-bottom: 0.95rem;
            border-bottom: 1px solid var(--qa-border);
        }
        .sidebar-brand-mark {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin-bottom: 0.35rem;
        }
        .sidebar-brand-mark span {
            width: 0.58rem;
            height: 0.58rem;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--qa-accent-alt), var(--qa-accent));
            box-shadow: 0 0 0 5px color-mix(in srgb, var(--qa-accent) 10%, transparent);
            flex: 0 0 auto;
        }
        .sidebar-brand-mark strong {
            color: var(--qa-text-strong);
            font-size: 1rem;
            font-weight: 760;
            letter-spacing: 0;
        }
        .sidebar-brand p {
            margin: 0;
            color: var(--qa-text-muted);
            font-size: 0.82rem;
            line-height: 1.45;
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
            font-size: clamp(2.1rem, 1.4rem + 3vw, 3.8rem) !important;
            line-height: 1.02 !important;
            letter-spacing: 0;
            margin: 0 0 1.25rem;
        }
        .qa-landing-hero p,
        .qa-story-panel p,
        .qa-feature-grid p,
        .qa-workflow h2 {
            color: var(--qa-text-muted);
            line-height: 1.68;
        }
        .qa-landing-hero p {
            font-size: 0.96rem !important;
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
            background: linear-gradient(135deg, var(--qa-accent-alt), var(--qa-accent), var(--qa-accent-warm));
            box-shadow: 0 16px 42px color-mix(in srgb, var(--qa-accent) 22%, transparent);
        }
        .qa-button-secondary {
            color: var(--qa-accent) !important;
            border: 1px solid var(--qa-border-strong);
            background: linear-gradient(
                135deg,
                color-mix(in srgb, var(--qa-accent) 10%, transparent),
                color-mix(in srgb, var(--qa-accent-alt) 6%, transparent)
            );
            box-shadow: 0 10px 28px color-mix(in srgb, var(--qa-accent) 10%, transparent);
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
        .qa-workflow {
            border: 1px solid var(--qa-border);
            border-radius: 8px;
            background: var(--qa-surface);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), var(--qa-shadow);
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
            border: 1px solid var(--qa-border-strong);
            border-radius: 8px;
            overflow: hidden;
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.08), transparent 24%),
                linear-gradient(135deg, color-mix(in srgb, var(--qa-accent) 10%, transparent), color-mix(in srgb, var(--qa-accent-alt) 8%, transparent)),
                color-mix(in srgb, var(--qa-surface-strong) 92%, var(--qa-bg) 8%);
            box-shadow: 0 28px 90px rgba(0, 0, 0, 0.46), inset 0 1px 0 rgba(255, 255, 255, 0.09);
            transform: rotateX(4deg) rotateY(-7deg);
            animation: qa-float 7.5s cubic-bezier(0.42, 0, 0.58, 1) infinite alternate;
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
            animation: qa-draw-line 5.8s cubic-bezier(0.42, 0, 0.58, 1) infinite alternate 350ms;
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
        .qa-story-section {
            margin-bottom: 3rem;
            padding: 1.9rem 0 2.1rem;
            border-top: 1px solid color-mix(in srgb, var(--qa-border) 80%, transparent);
            border-bottom: 1px solid color-mix(in srgb, var(--qa-border) 80%, transparent);
            background: transparent !important;
        }
        .qa-story-panel {
            display: grid;
            grid-template-columns: minmax(0, 0.9fr) minmax(320px, 1.1fr);
            gap: clamp(1.8rem, 4vw, 5rem);
            align-items: center;
            padding: 0;
            margin-bottom: 0;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        .qa-story-panel > div {
            max-width: 31rem;
            padding-left: 1rem;
            border-left: 2px solid color-mix(in srgb, var(--qa-accent) 45%, transparent);
        }
        .qa-story-panel h2,
        .qa-feature-section h2 {
            color: #eef7ff;
            font-size: clamp(1.55rem, 1.1rem + 2vw, 2.7rem) !important;
            line-height: 1.08 !important;
            margin: 0;
        }
        .qa-story-panel p {
            margin: 0;
            font-size: 0.96rem !important;
            max-width: 40rem;
            line-height: 1.75;
            color: var(--qa-text-soft);
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
        .qa-feature-link {
            display: block;
            color: inherit !important;
            text-decoration: none !important;
        }
        .qa-feature-grid article {
            min-height: 12.5rem;
            padding: 1.25rem;
            position: relative;
            overflow: hidden;
            transition: transform 260ms cubic-bezier(0.22, 1, 0.36, 1), border-color 260ms ease, box-shadow 260ms ease;
        }
        .qa-feature-grid article:hover {
            transform: translateY(-5px);
            border-color: var(--qa-border-strong);
            box-shadow: 0 16px 34px color-mix(in srgb, var(--qa-accent) 12%, transparent);
        }
        .qa-feature-grid article:after {
            content: "";
            position: absolute;
            left: 1.25rem;
            right: 1.25rem;
            bottom: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--qa-accent), var(--qa-accent-alt), var(--qa-accent-warm));
            animation: qa-accent-line 3.8s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite alternate;
        }
        .qa-feature-grid span {
            display: block;
            color: #2fffb2;
            font-family: "Source Code Pro", monospace;
            font-size: 0.82rem;
            margin-bottom: 1.2rem;
        }
        .qa-feature-grid h3 {
            color: #eef7ff;
            font-size: 1.04rem;
            margin: 0 0 0.4rem;
        }
        .qa-feature-grid p {
            margin: 0;
            font-size: 0.9rem;
            line-height: 1.55;
        }
        .qa-workflow {
            padding: clamp(1.35rem, 4vw, 2rem);
            margin-bottom: 2.2rem;
        }
        .qa-workflow h2 {
            color: #eef7ff;
            font-size: clamp(1.2rem, 1rem + 1vw, 1.75rem) !important;
            line-height: 1.18;
            margin: 0;
            max-width: 60rem;
        }
        @keyframes qa-pulse {
            0% { box-shadow: 0 0 0 0 rgba(47, 255, 178, 0.18); }
            100% { box-shadow: 0 0 0 8px rgba(47, 255, 178, 0); }
        }
        @keyframes qa-float {
            0% { transform: rotateX(4deg) rotateY(-7deg) translateY(0); }
            100% { transform: rotateX(3deg) rotateY(-5deg) translateY(-8px); }
        }
        @keyframes qa-draw-line {
            0% { stroke-dashoffset: 0.85; }
            100% { stroke-dashoffset: -0.85; }
        }
        @keyframes qa-background-drift {
            0% { background-position: 0% 0%, 0% 0%, 0% 0%, 0% 0%; }
            100% { background-position: 2% -2%, -2% 2%, 1% 1%, 0% 0%; }
        }
        @keyframes qa-sheen {
            0% { transform: translateX(-120%); opacity: 0; }
            25% { opacity: 0.10; }
            75% { opacity: 0.10; }
            100% { transform: translateX(120%); opacity: 0; }
        }
        @keyframes qa-accent-line {
            0% { transform: translateX(-12px) scaleX(0.96); opacity: 0.62; }
            100% { transform: translateX(12px) scaleX(1.04); opacity: 1; }
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
            font-size: clamp(1.35rem, 1rem + 1.3vw, 1.9rem);
            font-weight: 760;
            margin: 0;
            letter-spacing: 0;
            line-height: 1.15;
        }
        .hero-subtitle {
            color: #cbd5e1;
            font-size: 0.9rem !important;
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
            font-size: clamp(1.1rem, 0.95rem + 0.9vw, 1.45rem);
            font-weight: 760;
            line-height: 1.1;
            margin: 0;
            overflow-wrap: anywhere;
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
            font-size: clamp(0.95rem, 0.9rem + 0.25vw, 1rem);
            color: #f8fafc;
        }
        .dashboard-card p {
            margin: 0;
            color: #94a3b8;
            font-size: clamp(0.84rem, 0.8rem + 0.2vw, 0.88rem);
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
        .options-chain-panel {
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 14px;
            padding: 1rem 1.05rem 0.35rem;
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.92), rgba(8, 14, 28, 0.88));
            box-shadow: 0 18px 40px rgba(2, 6, 23, 0.28);
            margin-bottom: 0.75rem;
        }
        .options-chain-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.85rem;
        }
        .options-chain-header h3 {
            margin: 0;
            color: #f8fafc;
            font-size: 0.98rem !important;
            font-weight: 750;
        }
        .options-chain-header p {
            margin: 0.28rem 0 0;
            color: #94a3b8;
            font-size: 0.82rem !important;
            line-height: 1.45;
            max-width: 42rem;
        }
        .options-chain-hint {
            border: 1px dashed rgba(81, 215, 255, 0.28);
            border-radius: 10px;
            padding: 0.55rem 0.75rem;
            color: #cbd5e1;
            font-size: 0.82rem;
            background: rgba(81, 215, 255, 0.06);
            margin-bottom: 0.85rem;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 12px;
            overflow: hidden;
            background: rgba(2, 6, 23, 0.55);
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
            font-size: 0.9rem !important;
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
            .block-container {
                width: min(1180px, calc(100vw - 2.2rem));
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
                font-size: clamp(1.8rem, 9vw, 2.6rem) !important;
            }
            .block-container {
                width: min(1180px, calc(100vw - 1.4rem));
                padding-top: 1.05rem;
                padding-bottom: 2rem;
            }
            .hero-subtitle,
            .qa-landing-hero p,
            .qa-story-panel p,
            .qa-feature-grid p,
            .qa-workflow h2 {
                max-width: 100%;
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
        html, body, p, li, label, span, div, .stMarkdown, .stCaption {
            color: var(--qa-text);
        }
        .stMarkdown a {
            color: var(--qa-accent);
        }
        [data-testid="stAppViewContainer"] {
            background: transparent;
        }
        [data-testid="stToolbar"] {
            color: var(--qa-text-muted);
        }
        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input,
        div[data-baseweb="select"] > div,
        div[data-baseweb="popover"] [role="listbox"] {
            background: var(--qa-surface-strong) !important;
            color: var(--qa-text) !important;
        }
        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        div[data-baseweb="input"],
        div[data-baseweb="base-input"],
        div[data-baseweb="select"] > div {
            border-color: var(--qa-border) !important;
        }
        .stTextInput label,
        .stNumberInput label,
        .stDateInput label,
        .stSelectbox label,
        .stCheckbox label,
        .stRadio label,
        .stSlider label,
        .stMultiSelect label {
            color: var(--qa-text-muted) !important;
        }
        .stButton > button[kind="primary"],
        button[kind="primary"] {
            background: linear-gradient(
                135deg,
                var(--qa-accent-alt),
                var(--qa-accent),
                var(--qa-accent-warm)
            ) !important;
            border-color: color-mix(in srgb, var(--qa-accent) 68%, white 32%) !important;
            color: #03120c !important;
            box-shadow:
                0 12px 24px color-mix(in srgb, var(--qa-accent) 16%, transparent),
                inset 0 1px 0 rgba(255, 255, 255, 0.26) !important;
            position: relative;
            overflow: hidden;
            transition: transform 260ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 260ms ease, filter 260ms ease !important;
        }
        .stButton > button[kind="primary"]:hover,
        button[kind="primary"]:hover {
            background: linear-gradient(
                135deg,
                color-mix(in srgb, var(--qa-accent-alt) 88%, white 12%),
                color-mix(in srgb, var(--qa-accent) 88%, white 12%),
                color-mix(in srgb, var(--qa-accent-warm) 88%, white 12%)
            ) !important;
            border-color: color-mix(in srgb, var(--qa-accent) 74%, white 26%) !important;
            transform: translateY(-1px);
            box-shadow:
                0 16px 30px color-mix(in srgb, var(--qa-accent) 20%, transparent),
                inset 0 1px 0 rgba(255, 255, 255, 0.28) !important;
            filter: saturate(1.04);
        }
        .stButton > button[kind="primary"]::after,
        button[kind="primary"]::after {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(
                105deg,
                transparent 0%,
                rgba(255, 255, 255, 0.00) 38%,
                rgba(255, 255, 255, 0.22) 50%,
                rgba(255, 255, 255, 0.00) 62%,
                transparent 100%
            );
            pointer-events: none;
            animation: qa-sheen 4.6s ease-in-out infinite;
        }
        .stFormSubmitButton > button {
            background: color-mix(in srgb, var(--qa-accent) 12%, var(--qa-surface-strong) 88%) !important;
            border: 1px solid var(--qa-border-strong) !important;
            color: var(--qa-text-strong) !important;
            box-shadow: 0 8px 18px color-mix(in srgb, var(--qa-accent) 10%, transparent) !important;
            position: relative;
            overflow: hidden;
            transition: transform 240ms cubic-bezier(0.22, 1, 0.36, 1), background 240ms ease, border-color 240ms ease !important;
        }
        .stFormSubmitButton > button:hover {
            background: color-mix(in srgb, var(--qa-accent) 18%, var(--qa-surface-strong) 82%) !important;
            border-color: color-mix(in srgb, var(--qa-accent) 72%, white 28%) !important;
            transform: translateY(-1px);
        }
        .stFormSubmitButton > button::after {
            display: none !important;
        }
        [data-testid="stPlotlyChart"] {
            border: 1px solid var(--qa-border);
            border-radius: 14px;
            background:
                linear-gradient(180deg, color-mix(in srgb, var(--qa-accent) 4%, transparent), transparent 24%),
                var(--qa-surface);
            padding: 0.55rem 0.55rem 0.25rem;
            box-shadow: var(--qa-shadow);
            overflow: hidden;
        }
        [data-testid="stPlotlyChart"] > div {
            border-radius: 12px;
            overflow: hidden;
        }
        [data-testid="stPlotlyChart"] svg,
        [data-testid="stPlotlyChart"] canvas {
            border-radius: 12px;
        }
        .hero-panel,
        .kpi-card,
        .empty-state,
        .dashboard-card,
        .workflow-strip,
        .options-chain-panel,
        .qa-feature-grid article,
        .qa-hero-stats div,
        .qa-mini-grid div,
        div[data-testid="stMetric"],
        div[data-testid="stDataFrame"],
        .stTabs [data-baseweb="tab"],
        .qa-dashboard-preview,
        .qa-ticker-row span,
        .qa-chart-panel {
            background: var(--qa-surface) !important;
            border-color: var(--qa-border) !important;
            box-shadow: var(--qa-shadow);
        }
        .qa-story-panel,
        .qa-story-panel > div,
        .qa-story-panel p {
            background: transparent !important;
            box-shadow: none !important;
            border-color: transparent !important;
        }
        .hero-panel {
            background:
                linear-gradient(135deg, color-mix(in srgb, var(--qa-accent) 14%, transparent), transparent 55%),
                var(--qa-surface) !important;
        }
        .hero-kicker,
        .module-tag,
        .status-pill,
        .workflow-index,
        .options-chain-hint strong,
        .qa-section-kicker,
        .qa-eyebrow,
        .qa-feature-grid span {
            color: var(--qa-accent) !important;
        }
        .hero-title,
        .kpi-value,
        .dashboard-card h4,
        .options-chain-header h3,
        .qa-landing-hero h1,
        .qa-story-panel h2,
        .qa-feature-section h2,
        .qa-feature-grid h3,
        .qa-panel-heading strong,
        .qa-mini-grid strong,
        .qa-hero-stats strong {
            color: var(--qa-text-strong) !important;
        }
        .hero-subtitle,
        .kpi-label,
        .kpi-note,
        .dashboard-card p,
        .section-label,
        .workflow-step,
        .options-chain-header p,
        .options-chain-hint,
        .qa-hero-stats span,
        .qa-mini-grid small,
        .qa-panel-heading span,
        .qa-mini-grid span,
        .qa-window-bar,
        .app-subtitle {
            color: var(--qa-text-muted) !important;
        }
        .status-pill {
            border-color: var(--qa-border-strong) !important;
            background: var(--qa-accent-soft) !important;
        }
        .dashboard-card:before {
            background: var(--qa-accent) !important;
        }
        .delta-positive {
            color: var(--qa-success) !important;
        }
        .delta-negative {
            color: var(--qa-danger) !important;
        }
        .stTabs [data-baseweb="tab"] {
            background: var(--qa-surface-strong) !important;
            color: var(--qa-text) !important;
            border: 1px solid var(--qa-border) !important;
            border-bottom: none !important;
        }
        .stTabs [aria-selected="true"] {
            border-bottom: 2px solid var(--qa-accent) !important;
            color: var(--qa-text-strong) !important;
        }
        .qa-feature-grid article:hover,
        .qa-feature-link:focus-visible article {
            border-color: var(--qa-border-strong) !important;
        }
        .qa-feature-grid article:after {
            background: linear-gradient(90deg, var(--qa-accent), var(--qa-accent-alt), var(--qa-accent-warm)) !important;
        }
        .qa-window-bar i:nth-child(3) {
            background: var(--qa-accent-alt);
        }
        .qa-grid path {
            stroke: color-mix(in srgb, var(--qa-text-muted) 24%, transparent) !important;
        }
        .stAlert {
            background: var(--qa-surface) !important;
            border-color: var(--qa-border) !important;
        }
        section[data-testid="stSidebar"] button[kind="primary"],
        section[data-testid="stSidebar"] button[kind="primary"] * {
            color: var(--qa-text-strong) !important;
        }
        section[data-testid="stSidebar"] button[kind="primary"]::after {
            display: none !important;
        }
        section[data-testid="stSidebar"] button[kind="secondary"] * {
            color: var(--qa-text-muted) !important;
        }
        section[data-testid="stSidebar"] [data-testid="stExpander"] {
            border: 1px solid var(--qa-border);
            border-radius: 10px;
            background: var(--qa-surface);
            overflow: hidden;
        }
        section[data-testid="stSidebar"] [data-testid="stExpander"] details summary {
            color: var(--qa-text-strong) !important;
            font-weight: 650;
        }
        section[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stVerticalBlock"] {
            gap: 0.55rem;
        }
        .kpi-card,
        .dashboard-card,
        .qa-hero-stats div,
        .qa-mini-grid div,
        .options-chain-panel,
        div[data-testid="stMetric"] {
            transition: transform 240ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 240ms ease, border-color 240ms ease;
        }
        .kpi-card:hover,
        .dashboard-card:hover,
        .qa-hero-stats div:hover,
        .qa-mini-grid div:hover,
        .options-chain-panel:hover,
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: var(--qa-border-strong) !important;
            box-shadow:
                0 16px 30px color-mix(in srgb, var(--qa-accent) 10%, transparent),
                var(--qa-shadow) !important;
        }
        .status-pill {
            animation: qa-pulse 2.8s infinite;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
