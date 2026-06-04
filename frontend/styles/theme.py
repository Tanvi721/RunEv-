from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


DESIGN_TOKENS = {
    "dark": {
        "background": "#0b1220",
        "surface": "#111827",
        "surface_secondary": "#172033",
        "card": "#1e293b",
        "border": "rgba(148, 163, 184, 0.22)",
        "divider": "rgba(148, 163, 184, 0.16)",
        "text_primary": "#f8fafc",
        "text_secondary": "#cbd5e1",
        "text_muted": "#94a3b8",
        "accent": "#14e6b0",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#3b82f6",
        "gradient_start": "#14e6b0",
        "gradient_end": "#6366f1",
    },
    "light": {
        "background": "#f6f8fb",
        "surface": "#ffffff",
        "surface_secondary": "#eef3f8",
        "card": "#ffffff",
        "border": "rgba(15, 23, 42, 0.14)",
        "divider": "rgba(15, 23, 42, 0.10)",
        "text_primary": "#0f172a",
        "text_secondary": "#334155",
        "text_muted": "#64748b",
        "accent": "#059669",
        "success": "#059669",
        "warning": "#b45309",
        "error": "#dc2626",
        "info": "#2563eb",
        "gradient_start": "#10b981",
        "gradient_end": "#2563eb",
    },
}


def configure_page(title: str, icon: str = "⚡") -> None:
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

            :root {
                --runev-bg: #0f172a;
                --runev-panel: #111827;
                --runev-card: #1e293b;
                --runev-card-soft: rgba(30, 41, 59, 0.78);
                --runev-border: rgba(148, 163, 184, 0.18);
                --runev-green: #00e5a8;
                --runev-blue: #3b82f6;
                --runev-text: #f8fafc;
                --runev-muted: #94a3b8;
                --runev-warn: #f59e0b;
                --runev-danger: #ef4444;
                --runev-gold: #fbbf24;
                --runev-pink: #fb7185;
                --runev-violet: #a78bfa;
                --runev-shadow: 0 24px 80px rgba(2, 6, 23, 0.34);
            }

            html, body, [class*="css"] {
                font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }

            html, body, .stApp {
                max-width: 100%;
                overflow-x: hidden;
            }

            body, .stApp {
                background:
                    linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.92)),
                    radial-gradient(circle at 16% 10%, rgba(0, 229, 168, 0.14), transparent 26rem),
                    radial-gradient(circle at 78% 14%, rgba(251, 191, 36, 0.11), transparent 24rem),
                    radial-gradient(circle at 92% 72%, rgba(251, 113, 133, 0.10), transparent 22rem),
                    var(--runev-bg);
                color: var(--runev-text);
            }

            footer, #MainMenu { visibility: hidden; }
            [data-testid="stHeader"] {
                display: block !important;
                visibility: visible !important;
                height: 0 !important;
                background: transparent !important;
                pointer-events: none !important;
            }
            [data-testid="stDecoration"] { display: none; }
            [data-testid="stToolbar"],
            [data-testid="stDeployButton"],
            [data-testid="stBaseButton-header"],
            [data-testid="stStatusWidget"],
            .stDeployButton,
            header {
                display: none !important;
                visibility: hidden !important;
            }
            [data-testid="collapsedControl"] {
                display: flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                position: fixed !important;
                left: 0.75rem !important;
                top: 0.8rem !important;
                z-index: 999999 !important;
                pointer-events: auto !important;
            }

            [data-testid="collapsedControl"] button,
            [data-testid="stSidebarCollapseButton"] button,
            [data-testid="stSidebarCollapseButton"] {
                display: inline-flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                pointer-events: auto !important;
                min-width: 2.5rem !important;
                min-height: 2.5rem !important;
                border-radius: 999px !important;
                transition: transform 180ms ease, box-shadow 180ms ease, background 180ms ease !important;
            }

            [data-testid="collapsedControl"] button:focus-visible,
            [data-testid="stSidebarCollapseButton"] button:focus-visible,
            .runev-sidebar-float:focus-visible {
                outline: 3px solid rgba(0, 229, 168, 0.74) !important;
                outline-offset: 3px !important;
            }

            .block-container {
                width: 100%;
                max-width: min(1440px, 100%);
                box-sizing: border-box;
                padding: 1.1rem 1.6rem 3rem;
            }

            [data-testid="stHorizontalBlock"],
            [data-testid="column"] {
                min-width: 0;
            }

            [data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, rgba(15, 23, 42, 0.97), rgba(30, 41, 59, 0.96)),
                    radial-gradient(circle at top, rgba(0, 229, 168, 0.16), transparent 18rem);
                border-right: 1px solid var(--runev-border);
                transition: transform 220ms ease, margin-left 220ms ease, width 220ms ease, min-width 220ms ease;
                will-change: transform;
            }

            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] span {
                color: var(--runev-text);
            }

            h1, h2, h3 {
                letter-spacing: 0;
                color: var(--runev-text);
            }

            p, span, label, div {
                color: inherit;
            }

            [data-testid="stMarkdownContainer"],
            [data-testid="stMarkdownContainer"] p,
            [data-testid="stMarkdownContainer"] span,
            [data-testid="stCaptionContainer"],
            [data-testid="stCaptionContainer"] p,
            .stRadio label,
            .stRadio label span,
            .stCheckbox label,
            .stCheckbox label span,
            .stTextInput label,
            .stNumberInput label,
            .stSelectbox label,
            .stFileUploader label,
            .stTextArea label {
                color: #f8fafc !important;
                opacity: 1 !important;
            }

            .stCaptionContainer, .stCaptionContainer * {
                color: #cbd5e1 !important;
            }

            [data-testid="stAlert"],
            [data-testid="stAlert"] *,
            div[data-testid="stExpander"] *,
            div[data-testid="stForm"] * {
                color: #f8fafc !important;
            }

            [data-testid="stAlert"] {
                background: rgba(59, 130, 246, 0.20);
                border: 1px solid rgba(147, 197, 253, 0.35);
                border-radius: 14px;
            }

            .runev-notification {
                position: fixed;
                right: 1.25rem;
                top: 1.25rem;
                z-index: 999999;
                width: min(360px, calc(100vw - 2rem));
                padding: 1rem 1.1rem;
                border-radius: 14px;
                border: 1px solid rgba(255, 255, 255, 0.22);
                color: #f8fafc;
                box-shadow: 0 22px 54px rgba(2, 6, 23, 0.45);
                pointer-events: none;
                animation: runevNotify 5s ease both;
                font-weight: 750;
            }

            .runev-notification-title {
                font-size: 0.78rem;
                text-transform: uppercase;
                color: rgba(248, 250, 252, 0.78);
                margin-bottom: 0.25rem;
            }

            .runev-notification-info { background: linear-gradient(135deg, #2563eb, #0f172a); }
            .runev-notification-success { background: linear-gradient(135deg, #059669, #0f172a); }
            .runev-notification-warning { background: linear-gradient(135deg, #d97706, #0f172a); }
            .runev-notification-error { background: linear-gradient(135deg, #dc2626, #0f172a); }

            .sample-qr {
                display: grid;
                grid-template-columns: repeat(10, 10px);
                grid-template-rows: repeat(10, 10px);
                gap: 3px;
                width: max-content;
                padding: 12px;
                margin-top: 0.9rem;
                background: #f8fafc;
                border-radius: 12px;
                border: 5px solid #e2e8f0;
                box-shadow: 0 16px 34px rgba(2, 6, 23, 0.28);
            }

            .sample-qr div { background: #f8fafc; border-radius: 2px; }
            .sample-qr div:nth-child(1), .sample-qr div:nth-child(2), .sample-qr div:nth-child(3),
            .sample-qr div:nth-child(11), .sample-qr div:nth-child(13), .sample-qr div:nth-child(21),
            .sample-qr div:nth-child(22), .sample-qr div:nth-child(23),
            .sample-qr div:nth-child(8), .sample-qr div:nth-child(9), .sample-qr div:nth-child(10),
            .sample-qr div:nth-child(18), .sample-qr div:nth-child(20), .sample-qr div:nth-child(28),
            .sample-qr div:nth-child(29), .sample-qr div:nth-child(30),
            .sample-qr div:nth-child(81), .sample-qr div:nth-child(82), .sample-qr div:nth-child(83),
            .sample-qr div:nth-child(91), .sample-qr div:nth-child(93),
            .sample-qr div:nth-child(35), .sample-qr div:nth-child(37), .sample-qr div:nth-child(44),
            .sample-qr div:nth-child(45), .sample-qr div:nth-child(49), .sample-qr div:nth-child(52),
            .sample-qr div:nth-child(56), .sample-qr div:nth-child(58), .sample-qr div:nth-child(64),
            .sample-qr div:nth-child(67), .sample-qr div:nth-child(70), .sample-qr div:nth-child(74),
            .sample-qr div:nth-child(76), .sample-qr div:nth-child(78), .sample-qr div:nth-child(85),
            .sample-qr div:nth-child(88), .sample-qr div:nth-child(96), .sample-qr div:nth-child(99) {
                background: #0f172a;
            }

            .stButton > button, .stFormSubmitButton > button, div[data-testid="stDownloadButton"] > button {
                border: 1px solid rgba(0, 229, 168, 0.35);
                background: linear-gradient(135deg, var(--runev-green), var(--runev-blue), var(--runev-violet));
                color: #03111f;
                border-radius: 12px;
                font-weight: 800;
                min-height: 2.7rem;
                box-shadow: 0 14px 34px rgba(0, 229, 168, 0.18);
                transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
            }

            .stButton > button:hover, .stFormSubmitButton > button:hover {
                transform: translateY(-1px);
                filter: brightness(1.05);
                box-shadow: 0 18px 44px rgba(59, 130, 246, 0.24);
            }

            .stButton > button:disabled {
                background: #334155;
                color: #94a3b8;
                border-color: rgba(148, 163, 184, 0.14);
                box-shadow: none;
            }

            div[role="radiogroup"] {
                gap: 0.55rem;
            }

            .runev-sidebar-brand {
                padding: 1rem 0 1.5rem;
                margin-bottom: 1rem;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            }

            .runev-sidebar-logo {
                font-size: 1.55rem;
                font-weight: 800;
                letter-spacing: -0.04em;
                color: var(--runev-text);
                margin-bottom: 0.35rem;
            }

            .runev-sidebar-subtitle {
                color: var(--runev-text-secondary);
                font-size: 0.92rem;
                margin: 0;
                line-height: 1.5;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(17, 24, 39, 0.96));
                border-right: 1px solid rgba(255, 255, 255, 0.08);
                padding-top: 1.4rem;
            }

            [data-testid="stSidebar"] .stRadio label {
                display: block;
                border-radius: 14px;
                padding: 0.9rem 0.95rem;
                background: rgba(255, 255, 255, 0.04);
                color: var(--runev-text);
                font-weight: 600;
                margin-bottom: 0.45rem;
                transition: background 200ms ease, transform 200ms ease, border-color 200ms ease;
            }

            [data-testid="stSidebar"] .stRadio label:hover {
                background: rgba(255, 255, 255, 0.08);
                transform: translateY(-1px);
            }

            [data-testid="stSidebar"] .stRadio label.stRadio > input:checked + * {
                border-color: rgba(0, 229, 168, 0.42) !important;
                background: rgba(0, 229, 168, 0.12) !important;
            }

            [data-testid="stSidebar"] .stButton > button,
            [data-testid="stSidebar"] .stFormSubmitButton > button {
                border-radius: 14px;
            }

            div[role="radiogroup"] label {
                min-height: 44px;
                padding: 0.55rem 0.8rem;
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 999px;
                background: rgba(15, 23, 42, 0.62);
                transition: border-color 160ms ease, background 160ms ease, transform 160ms ease;
            }

            div[role="radiogroup"] label:hover {
                transform: translateY(-1px);
                border-color: rgba(0, 229, 168, 0.42);
                background: rgba(30, 41, 59, 0.78);
            }

            div[role="radiogroup"] label:has(input:checked) {
                border-color: rgba(0, 229, 168, 0.72);
                background: rgba(0, 229, 168, 0.12);
                box-shadow: 0 0 0 1px rgba(0, 229, 168, 0.12) inset;
            }

            .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div,
            .stTextArea textarea {
                background: rgba(15, 23, 42, 0.8);
                border: 1px solid var(--runev-border);
                border-radius: 12px;
                color: var(--runev-text) !important;
                -webkit-text-fill-color: var(--runev-text) !important;
                opacity: 1 !important;
            }

            .stTextInput input:disabled {
                color: #e2e8f0 !important;
                -webkit-text-fill-color: #e2e8f0 !important;
                opacity: 1 !important;
            }

            div[data-testid="stMetric"] {
                background: linear-gradient(145deg, rgba(30, 41, 59, 0.82), rgba(15, 23, 42, 0.7));
                border: 1px solid var(--runev-border);
                border-radius: 16px;
                padding: 1rem;
                box-shadow: var(--runev-shadow);
            }

            div[data-testid="stMetricLabel"] p { color: var(--runev-muted); font-weight: 700; }
            div[data-testid="stMetricValue"] { color: var(--runev-text); }

            .runev-hero {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                padding: 1.2rem 1.4rem;
                margin-bottom: 1rem;
                border: 1px solid var(--runev-border);
                border-radius: 22px;
                background:
                    linear-gradient(135deg, rgba(0, 229, 168, 0.16), rgba(59, 130, 246, 0.12), rgba(251, 191, 36, 0.08)),
                    rgba(15, 23, 42, 0.72);
                box-shadow: var(--runev-shadow);
                animation: runevFade 420ms ease both;
            }

            .runev-eyebrow {
                color: var(--runev-green);
                font-weight: 800;
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }

            .runev-title {
                margin: 0.18rem 0 0;
                font-size: clamp(1.7rem, 3vw, 3.2rem);
                font-weight: 850;
                line-height: 1.04;
            }

            .runev-subtitle {
                color: #cbd5e1;
                margin: 0.5rem 0 0;
                max-width: 820px;
            }

            .runev-card, div[data-testid="stExpander"] {
                background:
                    linear-gradient(145deg, rgba(30, 41, 59, 0.90), rgba(17, 24, 39, 0.78)),
                    var(--runev-card-soft);
                border: 1px solid var(--runev-border);
                border-radius: 18px;
                padding: 1rem;
                box-shadow: var(--runev-shadow);
                transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
                animation: runevRise 360ms ease both;
            }

            .runev-card:hover {
                transform: translateY(-2px);
                border-color: rgba(0, 229, 168, 0.34);
                background: rgba(30, 41, 59, 0.92);
            }

            .block-container:has(.runev-auth-page) {
                width: 100%;
                height: auto;
                min-height: 100vh;
                max-width: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 0;
                overflow: auto;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] {
                width: 100%;
                max-width: 1080px;
                margin: 0 auto;
                align-items: stretch;
                padding: 0 1.5rem;
                box-sizing: border-box;
            }

            .block-container:has(.runev-auth-page) [data-testid="column"]:has(.runev-auth-card-copy),
            .block-container:has(.runev-auth-page) [data-testid="column"]:nth-of-type(2) {
                max-width: 100%;
                width: 100%;
                padding: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 24px;
                background: rgba(8, 20, 31, 0.88);
                box-shadow: 
                    0 24px 80px rgba(2, 6, 23, 0.34),
                    0 2px 8px rgba(15, 23, 42, 0.12);
                backdrop-filter: blur(18px);
                transition: all 280ms ease;
            }

            .block-container:has(.runev-auth-page) [data-testid="column"]:has(.runev-auth-card-copy):hover,
            .block-container:has(.runev-auth-page) [data-testid="column"]:nth-of-type(2):hover {
                border-color: rgba(148, 163, 184, 0.26);
                box-shadow: 
                    0 12px 40px rgba(15, 23, 42, 0.16),
                    0 2px 8px rgba(15, 23, 42, 0.10);
                transform: translateY(-2px);
            }

            .runev-auth-heading {
                max-width: 44rem;
                margin-bottom: 1.5rem;
                padding: 2rem 2.25rem;
                border-radius: 28px;
                border: 1px solid rgba(255, 255, 255, 0.10);
                background: rgba(8, 20, 31, 0.92);
                box-shadow: 0 28px 80px rgba(2, 6, 23, 0.35);
                color: var(--runev-text);
            }

            .runev-auth-heading span,
            .runev-auth-card-copy span {
                display: block;
                color: var(--runev-green);
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                margin-bottom: 0.75rem;
                opacity: 0.9;
            }

            .runev-auth-heading h1 {
                margin: 0;
                font-size: clamp(2.2rem, 4vw, 3.8rem);
                line-height: 1.02;
                font-weight: 800;
                color: var(--runev-text);
            }

            .runev-auth-heading p {
                margin: 1rem 0 0;
                color: var(--runev-text-secondary);
                font-size: 1rem;
                line-height: 1.7;
                max-width: 40rem;
            }

            .runev-auth-card-copy {
                margin-bottom: 1.5rem;
                animation: runevFade 500ms ease both;
            }

            .runev-auth-card-copy h2 {
                margin: 0;
                font-size: 1.55rem;
                line-height: 1.3;
                font-weight: 700;
                color: #0f172a;
                letter-spacing: -0.01em;
            }

            .runev-auth-card-copy p {
                margin: 0.6rem 0 0;
                color: #64748b;
                line-height: 1.5;
                font-weight: 500;
                font-size: 0.95rem;
            }

            .runev-auth-legal {
                display: block;
                margin-top: 1.2rem;
                color: #94a3b8;
                font-size: 0.88rem;
            }

            .block-container:has(.runev-auth-page) [data-testid="stAlert"] {
                margin: 0.75rem 0 1rem;
                border-radius: 10px;
                background: #fef2f2;
                border: 1px solid #fecaca;
                box-shadow: none;
                color: #7f1d1d !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stAlert"][kind="error"] {
                background: #fef2f2;
                border-color: #fecaca;
                color: #7f1d1d !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stAlert"][kind="info"],
            .block-container:has(.runev-auth-page) [data-testid="stAlert"][kind="success"] {
                background: #f0f9ff;
                border-color: #bae6fd;
                color: #0c2d6d !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [data-testid="stTabBar"] {
                border-bottom: 1px solid rgba(255, 255, 255, 0.12);
                gap: 0;
                background: transparent;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] {
                background: transparent;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button {
                border: none;
                border-bottom: 2px solid transparent;
                color: #64748b;
                font-weight: 600;
                font-size: 0.95rem;
                padding: 0.85rem 0.8rem !important;
                transition: all 200ms ease;
                background: transparent !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button[aria-selected="true"] {
                color: #0f766e;
                border-bottom-color: #0f766e;
                background: transparent !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button:hover {
                color: #0f766e;
                border-color: transparent;
            }

            .block-container:has(.runev-auth-page) .stCheckbox label {
                display: flex;
                align-items: center;
                gap: 0.65rem;
                color: #475569;
                font-weight: 550;
                cursor: pointer;
                transition: all 200ms ease;
            }

            .block-container:has(.runev-auth-page) .stCheckbox label:hover {
                color: #0f766e;
            }

            .block-container:has(.runev-auth-page) .stTextInput input {
                min-height: 2.8rem;
                margin-top: 0.5rem;
                background: rgba(15, 23, 42, 0.96) !important;
                border: 1px solid rgba(255, 255, 255, 0.18) !important;
                border-radius: 14px !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-weight: 500;
                font-size: 0.95rem;
                padding: 0.9rem 1rem !important;
                transition: all 200ms ease !important;
                box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.04) !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input::placeholder {
                color: #94a3b8 !important;
                opacity: 1 !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input:hover {
                border-color: #cbd5e1 !important;
                box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08) !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input:focus {
                background: #ffffff !important;
                border-color: #0f766e !important;
                box-shadow: 
                    0 0 0 3px rgba(15, 118, 110, 0.1),
                    0 2px 8px rgba(15, 23, 42, 0.10) !important;
                outline: none !important;
            }

            .block-container:has(.runev-auth-page) .stButton > button,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button {
                min-height: 2.8rem;
                border-radius: 10px;
                font-size: 0.98rem;
                font-weight: 700;
                letter-spacing: 0.01em;
                background: linear-gradient(135deg, #14e6b0, #6366f1) !important;
                border: none !important;
                color: #ffffff !important;
                box-shadow: 0 4px 12px rgba(15, 118, 110, 0.2) !important;
                transition: all 200ms ease !important;
            }

            .block-container:has(.runev-auth-page) .stButton > button:hover,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(15, 118, 110, 0.28) !important;
                filter: brightness(1.08);
            }

            .block-container:has(.runev-auth-page) .stButton > button:active,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button:active {
                transform: translateY(0);
                box-shadow: 0 2px 6px rgba(15, 118, 110, 0.16) !important;
            }

            .block-container:has(.runev-auth-page) .stButton > button:disabled,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button:disabled {
                background: #e2e8f0 !important;
                color: #94a3b8 !important;
                border-color: transparent !important;
                box-shadow: none !important;
                transform: none;
                cursor: not-allowed;
            }

            .block-container:has(.runev-auth-page) .stButton > button:disabled:hover {
                filter: none;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > button,
            .block-container:has(.runev-auth-page) .stLinkButton > button {
                min-height: 2.8rem;
                border-radius: 10px;
                font-size: 0.98rem;
                font-weight: 700;
                letter-spacing: 0.01em;
                background: linear-gradient(135deg, #14e6b0, #6366f1) !important;
                border: none !important;
                color: #ffffff !important;
                box-shadow: 0 4px 12px rgba(15, 118, 110, 0.2) !important;
                transition: all 200ms ease !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > button:hover,
            .block-container:has(.runev-auth-page) .stLinkButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(15, 118, 110, 0.28) !important;
                filter: brightness(1.08);
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > button:disabled,
            .block-container:has(.runev-auth-page) .stLinkButton > button:disabled {
                background: #e2e8f0 !important;
                color: #94a3b8 !important;
                box-shadow: none !important;
                transform: none;
                cursor: not-allowed;
            }

            .block-container:has(.runev-auth-page) [data-testid="stCaptionContainer"],
            .block-container:has(.runev-auth-page) [data-testid="stCaptionContainer"] p {
                color: #64748b !important;
                font-size: 0.85rem !important;
                margin-top: 0.4rem !important;
            }

            .runev-auth-visual {
                display: block;
            }

            .block-container:has(.runev-driver-auth-page) {
                width: 100%;
                height: auto;
                min-height: 100vh;
                max-width: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 0;
                overflow: auto;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                width: 100%;
                max-width: 1080px;
                margin: 0 auto;
                align-items: stretch;
                padding: 0 1.5rem;
                box-sizing: border-box;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="column"]:has(.runev-driver-auth-copy),
            .block-container:has(.runev-driver-auth-page) [data-testid="column"]:nth-of-type(2) {
                max-width: 100%;
                width: 100%;
                padding: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 24px;
                background: rgba(8, 20, 31, 0.88);
                box-shadow: 
                    0 24px 80px rgba(2, 6, 23, 0.34),
                    0 2px 8px rgba(15, 23, 42, 0.12);
                backdrop-filter: blur(18px);
                transition: all 280ms ease;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="column"]:has(.runev-driver-auth-copy):hover,
            .block-container:has(.runev-driver-auth-page) [data-testid="column"]:nth-of-type(2):hover {
                border-color: rgba(148, 163, 184, 0.26);
                box-shadow: 
                    0 12px 40px rgba(15, 23, 42, 0.16),
                    0 2px 8px rgba(15, 23, 42, 0.10);
                transform: translateY(-2px);
            }

            .runev-driver-auth-heading {
                max-width: 42rem;
                margin-bottom: 1.5rem;
                padding: 2rem 2.25rem;
                border-radius: 28px;
                border: 1px solid rgba(255, 255, 255, 0.10);
                background: rgba(8, 20, 31, 0.92);
                box-shadow: 0 28px 80px rgba(2, 6, 23, 0.35);
                color: var(--runev-text);
            }

            .runev-driver-auth-heading span,
            .runev-driver-auth-copy span {
                display: block;
                color: var(--runev-green);
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                margin-bottom: 0.75rem;
                opacity: 0.9;
            }

            .runev-driver-auth-heading h1 {
                margin: 0;
                font-size: clamp(2rem, 3.4vw, 3.4rem);
                line-height: 1.02;
                font-weight: 800;
                color: var(--runev-text);
            }

            .runev-driver-auth-copy {
                margin-bottom: 1.5rem;
                animation: runevFade 500ms ease both;
            }

            .runev-driver-auth-copy h2 {
                margin: 0;
                font-size: 1.55rem;
                line-height: 1.3;
                font-weight: 700;
                color: #0f172a;
                letter-spacing: -0.01em;
            }

            .runev-driver-auth-copy p {
                margin: 0.6rem 0 0;
                color: #64748b;
                line-height: 1.5;
                font-weight: 500;
                font-size: 0.95rem;
            }

            .runev-auth-visual,
            .runev-driver-auth-visual {
                padding: 2rem;
                border-radius: 28px;
                background: rgba(8, 20, 31, 0.94);
                border: 1px solid rgba(255, 255, 255, 0.10);
                box-shadow: 0 30px 80px rgba(2, 6, 23, 0.32);
                color: var(--runev-text);
            }

            .runev-auth-visual h2,
            .runev-driver-auth-visual h2 {
                margin: 0;
                font-size: 1.95rem;
                line-height: 1.1;
                font-weight: 800;
                color: var(--runev-text);
                max-width: 32rem;
            }

            .runev-auth-visual p,
            .runev-driver-auth-visual p {
                margin: 1rem 0 0;
                color: var(--runev-text-secondary);
                line-height: 1.7;
                font-size: 0.98rem;
                max-width: 36rem;
            }

            .runev-auth-preview-grid,
            .runev-fleet-preview-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 1rem;
                margin-top: 1.5rem;
            }

            .runev-auth-preview-grid div,
            .runev-fleet-preview-grid div {
                padding: 1rem 1rem 1.1rem;
                border-radius: 18px;
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.08);
            }

            .runev-auth-preview-grid span,
            .runev-fleet-preview-grid span {
                display: block;
                color: #94a3b8;
                font-size: 0.82rem;
                margin-bottom: 0.55rem;
            }

            .runev-auth-preview-grid strong,
            .runev-fleet-preview-grid strong {
                display: block;
                font-size: 1.25rem;
                margin-bottom: 0.35rem;
            }

            .runev-auth-preview-grid b,
            .runev-fleet-preview-grid b {
                color: #94a3b8;
                font-size: 0.88rem;
                font-weight: 500;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="stForm"] {
                border: 0;
                padding: 0;
                background: transparent;
            }

            .block-container:has(.runev-driver-auth-page) .stTextInput {
                margin-bottom: 0.9rem;
            }

            .block-container:has(.runev-driver-auth-page) .stTextInput input {
                min-height: 2.8rem;
                border-radius: 14px !important;
                background: rgba(15, 23, 42, 0.95) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-weight: 500;
                font-size: 0.95rem;
                padding: 0.9rem 1rem !important;
                transition: all 200ms ease !important;
                box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03) !important;
            }

            .block-container:has(.runev-driver-auth-page) .stTextInput input::placeholder {
                color: rgba(248, 250, 252, 0.6) !important;
                opacity: 1 !important;
            }

            .block-container:has(.runev-driver-auth-page) .stTextInput input:hover {
                border-color: rgba(255, 255, 255, 0.20) !important;
                box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.06) !important;
            }

            .block-container:has(.runev-driver-auth-page) .stTextInput input:focus {
                background: rgba(15, 23, 42, 0.98) !important;
                border-color: #14e6b0 !important;
                box-shadow: 
                    0 0 0 3px rgba(20, 230, 176, 0.12),
                    inset 0 0 0 1px rgba(255, 255, 255, 0.06) !important;
                outline: none !important;
            }

            .block-container:has(.runev-driver-auth-page) .stButton > button,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button {
                min-height: 2.8rem;
                border-radius: 10px;
                font-size: 0.98rem;
                font-weight: 700;
                letter-spacing: 0.01em;
                background: linear-gradient(135deg, #14e6b0, #6366f1) !important;
                border: none !important;
                color: #ffffff !important;
                box-shadow: 0 4px 12px rgba(15, 118, 110, 0.2) !important;
                transition: all 200ms ease !important;
            }

            .block-container:has(.runev-driver-auth-page) .stButton > button:hover,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(15, 118, 110, 0.28) !important;
                filter: brightness(1.08);
            }

            .block-container:has(.runev-driver-auth-page) .stButton > button:active,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button:active {
                transform: translateY(0);
                box-shadow: 0 2px 6px rgba(15, 118, 110, 0.16) !important;
            }

            .block-container:has(.runev-driver-auth-page) .stButton > button:disabled,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button:disabled {
                background: #e2e8f0 !important;
                color: #94a3b8 !important;
                border-color: transparent !important;
                box-shadow: none !important;
                transform: none;
                cursor: not-allowed;
            }

            .block-container:has(.runev-driver-auth-page) .stButton > button:disabled:hover {
                filter: none;
                box-shadow: none !important;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="stAlert"] {
                margin: 0.75rem 0 1rem;
                border-radius: 10px;
                background: #fef2f2;
                border: 1px solid #fecaca;
                box-shadow: none;
                color: #7f1d1d !important;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="stAlert"][kind="error"] {
                background: #fef2f2;
                border-color: #fecaca;
                color: #7f1d1d !important;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="stAlert"][kind="info"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stAlert"][kind="success"] {
                background: #f0f9ff;
                border-color: #bae6fd;
                color: #0c2d6d !important;
            }

            .block-container:has(.runev-driver-auth-page) .stCheckbox label {
                display: flex;
                align-items: center;
                gap: 0.65rem;
                color: #475569;
                font-weight: 550;
                cursor: pointer;
                transition: all 200ms ease;
            }

            .block-container:has(.runev-driver-auth-page) .stCheckbox label:hover {
                color: #0f766e;
            }

            .block-container:has(.runev-driver-auth-page) .stTabs [data-testid="stTabBar"] {
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                gap: 0;
                background: transparent;
            }

            .block-container:has(.runev-driver-auth-page) .stTabs [role="tablist"] {
                background: transparent;
            }

            .block-container:has(.runev-driver-auth-page) .stTabs [role="tablist"] button {
                min-width: 10rem;
                border: none;
                border-bottom: 2px solid transparent;
                color: #cbd5e1;
                font-weight: 600;
                font-size: 0.95rem;
                padding: 0.85rem 0.8rem !important;
                transition: all 200ms ease;
                background: transparent !important;
            }

            .block-container:has(.runev-driver-auth-page) .stTabs [role="tablist"] button[aria-selected="true"] {
                color: #ffffff;
                border-bottom-color: #14e6b0;
                font-weight: 700;
            }

            .block-container:has(.runev-driver-auth-page) .stTabs [role="tablist"] button:hover {
                color: #ffffff;
            }

            .runev-driver-auth-visual {
                display: block;
            }

            .runev-driver-auth-visual h2,
            .runev-driver-auth-visual p {
                display: block;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="stLinkButton"] > button,
            .block-container:has(.runev-driver-auth-page) .stLinkButton > button {
                min-height: 2.8rem;
                border-radius: 10px;
                font-size: 0.98rem;
                font-weight: 700;
                letter-spacing: 0.01em;
                background: linear-gradient(135deg, #0f766e, #0d6b63) !important;
                border: none !important;
                color: #ffffff !important;
                box-shadow: 0 4px 12px rgba(15, 118, 110, 0.2) !important;
                transition: all 200ms ease !important;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="stLinkButton"] > button:hover,
            .block-container:has(.runev-driver-auth-page) .stLinkButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(15, 118, 110, 0.28) !important;
                filter: brightness(1.08);
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="stLinkButton"] > button:disabled,
            .block-container:has(.runev-driver-auth-page) .stLinkButton > button:disabled {
                background: #e2e8f0 !important;
                color: #94a3b8 !important;
                box-shadow: none !important;
                transform: none;
                cursor: not-allowed;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="stCaptionContainer"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stCaptionContainer"] p {
                color: #64748b !important;
                font-size: 0.85rem !important;
                margin-top: 0.4rem !important;
            }

            .runev-fleet-preview-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.65rem;
                margin-top: 1.25rem;
            }

            .runev-fleet-preview-grid div,
            .runev-driver-activity div {
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: 14px;
                background: rgba(15, 23, 42, 0.54);
                box-shadow: 0 14px 34px rgba(2, 6, 23, 0.20);
            }

            .runev-fleet-preview-grid div {
                padding: 0.85rem;
            }

            .runev-fleet-preview-grid span,
            .runev-driver-activity span {
                display: block;
                color: #94a3b8;
                font-size: 0.78rem;
                font-weight: 850;
            }

            .runev-fleet-preview-grid strong {
                display: block;
                margin-top: 0.25rem;
                color: var(--runev-text);
                font-size: 1.55rem;
                line-height: 1;
                font-weight: 950;
            }

            .runev-fleet-preview-grid b {
                display: block;
                margin-top: 0.38rem;
                color: var(--runev-green);
                font-size: 0.75rem;
            }

            .runev-driver-activity {
                display: grid;
                gap: 0.6rem;
                margin-top: 1rem;
            }

            .runev-driver-activity div {
                display: grid;
                grid-template-columns: auto minmax(0, 1fr) auto;
                align-items: center;
                gap: 0.7rem;
                padding: 0.75rem 0.85rem;
            }

            .runev-driver-activity i {
                width: 0.7rem;
                height: 0.7rem;
                border-radius: 999px;
                background: var(--runev-green);
                box-shadow: 0 0 0 7px rgba(0, 229, 168, 0.12);
            }

            .runev-driver-activity strong {
                color: var(--runev-text);
                font-size: 0.84rem;
                white-space: nowrap;
            }

            .runev-metric {
                position: relative;
                overflow: hidden;
                min-height: 138px;
            }

            .runev-metric::after {
                content: "";
                position: absolute;
                right: -3rem;
                top: -3rem;
                width: 8rem;
                height: 8rem;
                border-radius: 999px;
                background: linear-gradient(135deg, rgba(0, 229, 168, 0.18), rgba(251, 191, 36, 0.13), rgba(251, 113, 133, 0.10));
            }

            .runev-metric-icon { font-size: 1.65rem; }
            .runev-metric-label { color: #cbd5e1; font-weight: 800; margin-top: 0.8rem; }
            .runev-metric-value { font-size: 2rem; font-weight: 850; margin-top: 0.25rem; }
            .runev-metric-delta { color: var(--runev-green); font-weight: 800; font-size: 0.85rem; margin-top: 0.35rem; }

            .runev-bill-card, .runev-payable-card {
                background:
                    linear-gradient(145deg, rgba(30, 41, 59, 0.92), rgba(15, 23, 42, 0.78)),
                    var(--runev-card-soft);
                border: 1px solid var(--runev-border);
                border-radius: 18px;
                padding: 1rem;
                box-shadow: var(--runev-shadow);
            }

            .runev-bill-card-compact {
                padding: 0.9rem;
            }

            .runev-bill-top {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 0.75rem;
                margin-bottom: 0.9rem;
            }

            .runev-bill-top h3 {
                margin: 0.65rem 0 0;
                font-size: 1.35rem;
                line-height: 1.1;
            }

            .runev-bill-total {
                flex: 0 0 auto;
                font-size: clamp(1.7rem, 3vw, 2.6rem);
                line-height: 1;
                font-weight: 850;
                color: var(--runev-text);
                white-space: nowrap;
            }

            .runev-bill-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.7rem;
                margin-bottom: 1rem;
            }

            .runev-bill-grid div {
                min-width: 0;
                padding: 0.8rem;
                border: 1px solid var(--runev-border);
                border-radius: 14px;
                background: rgba(15, 23, 42, 0.52);
            }

            .runev-bill-grid span,
            .runev-bill-lines span,
            .runev-payable-card span {
                display: block;
                color: #cbd5e1;
                font-size: 0.82rem;
                font-weight: 800;
                margin-bottom: 0.35rem;
            }

            .runev-bill-grid strong {
                display: block;
                color: var(--runev-text);
                font-size: clamp(1rem, 1.8vw, 1.35rem);
                line-height: 1.15;
                overflow-wrap: anywhere;
            }

            .runev-bill-lines {
                display: grid;
                gap: 0.65rem;
            }

            .runev-bill-lines strong {
                display: block;
                color: var(--runev-text);
                font-size: 0.98rem;
                line-height: 1.35;
                overflow-wrap: anywhere;
            }

            .runev-payable-card {
                margin-bottom: 0.75rem;
            }

            .runev-payable-card strong {
                display: block;
                color: var(--runev-text);
                font-size: clamp(2rem, 4vw, 3rem);
                line-height: 1.05;
                font-weight: 850;
            }

            .runev-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                border-radius: 999px;
                padding: 0.28rem 0.68rem;
                font-size: 0.78rem;
                font-weight: 850;
                border: 1px solid rgba(148, 163, 184, 0.16);
                background: rgba(148, 163, 184, 0.12);
            }

            .badge-green { color: #03111f; background: #00e5a8; border-color: rgba(0, 229, 168, 0.5); }
            .badge-blue { color: #eff6ff; background: #2563eb; border-color: rgba(147, 197, 253, 0.5); }
            .badge-warn { color: #1f1300; background: #fbbf24; border-color: rgba(251, 191, 36, 0.5); }
            .badge-red { color: #fff1f2; background: #e11d48; border-color: rgba(251, 113, 133, 0.5); }

            .runev-trip {
                display: grid;
                grid-template-columns: 1.35fr 1fr auto;
                gap: 1rem;
                align-items: center;
            }

            .runev-timeline-wrap {
                position: relative;
                margin: 1rem 0 1.25rem;
                padding: 1rem;
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: 18px;
                background: rgba(15, 23, 42, 0.44);
                overflow: hidden;
            }

            .runev-timeline-line {
                position: absolute;
                left: 1.7rem;
                right: 1.7rem;
                top: 2.1rem;
                height: 3px;
                border-radius: 999px;
                background: rgba(51, 65, 85, 0.9);
            }

            .runev-timeline-line span {
                display: block;
                height: 100%;
                border-radius: inherit;
                background: linear-gradient(90deg, var(--runev-green), var(--runev-blue));
                box-shadow: 0 0 18px rgba(0, 229, 168, 0.42);
                transition: width 360ms ease;
            }

            .runev-timeline {
                position: relative;
                display: flex;
                justify-content: space-between;
                gap: 0.75rem;
                align-items: flex-start;
                margin: 0;
            }

            .runev-step {
                display: inline-flex;
                flex-direction: column;
                align-items: center;
                gap: 0.45rem;
                color: #cbd5e1;
                font-size: 0.76rem;
                font-weight: 800;
                text-align: center;
                max-width: 7.2rem;
            }

            .runev-step-dot {
                width: 1.45rem;
                height: 1.45rem;
                border-radius: 999px;
                background: #334155;
                display: grid;
                place-items: center;
                color: #cbd5e1;
                font-size: 0.7rem;
                border: 2px solid rgba(148, 163, 184, 0.32);
            }

            .runev-step-active .runev-step-dot, .runev-step-done .runev-step-dot {
                background: var(--runev-green);
                color: #03111f;
                border-color: rgba(0, 229, 168, 0.72);
                box-shadow: 0 0 0 7px rgba(0, 229, 168, 0.12), 0 0 24px rgba(0, 229, 168, 0.36);
            }

            .runev-step-active { color: var(--runev-text); }
            .runev-step-done { color: #e2e8f0; }
            .runev-kpi-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 1rem; }
            .runev-two-col { display: grid; grid-template-columns: minmax(0, 2fr) minmax(320px, 1fr); gap: 1rem; }

            .runev-driver-card,
            .runev-summary-card,
            .runev-pay-panel {
                margin-bottom: 1rem;
            }

            .runev-driver-top {
                display: grid;
                grid-template-columns: auto minmax(0, 1fr) auto;
                gap: 0.85rem;
                align-items: center;
                margin-bottom: 1rem;
            }

            .runev-avatar {
                width: 3.25rem;
                height: 3.25rem;
                border-radius: 18px;
                display: grid;
                place-items: center;
                color: #03111f;
                font-weight: 900;
                background: linear-gradient(135deg, var(--runev-green), var(--runev-blue));
                box-shadow: 0 18px 38px rgba(0, 229, 168, 0.18);
            }

            .runev-driver-name {
                color: var(--runev-text);
                font-size: 1.1rem;
                font-weight: 850;
            }

            .runev-driver-meta {
                color: #cbd5e1;
                font-weight: 700;
                margin-top: 0.15rem;
            }

            .runev-driver-grid,
            .runev-summary-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.75rem;
            }

            .runev-driver-grid div,
            .runev-summary-grid div {
                padding: 0.9rem;
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: 14px;
                background: rgba(15, 23, 42, 0.54);
            }

            .runev-driver-grid span,
            .runev-summary-grid span,
            .runev-summary-line span,
            .runev-upi-qr span {
                display: block;
                color: #94a3b8;
                font-size: 0.78rem;
                font-weight: 800;
                margin-bottom: 0.25rem;
            }

            .runev-driver-grid strong,
            .runev-summary-grid strong,
            .runev-summary-line strong,
            .runev-upi-qr strong {
                display: block;
                color: var(--runev-text);
                font-weight: 850;
                overflow-wrap: anywhere;
            }

            .runev-section-kicker {
                color: var(--runev-green);
                font-size: 0.78rem;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }

            .runev-summary-card h3 {
                margin: 0.35rem 0 1rem;
                font-size: clamp(1.45rem, 2.4vw, 2rem);
            }

            .runev-summary-line {
                display: flex;
                justify-content: space-between;
                gap: 1rem;
                margin-top: 0.85rem;
                padding-top: 0.85rem;
                border-top: 1px solid rgba(148, 163, 184, 0.14);
            }

            .runev-pay-panel {
                position: relative;
                overflow: hidden;
                background:
                    linear-gradient(145deg, rgba(0, 229, 168, 0.13), rgba(59, 130, 246, 0.08)),
                    rgba(15, 23, 42, 0.84);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 18px;
                padding: 1.05rem 1.15rem;
                box-shadow: 0 18px 48px rgba(2, 6, 23, 0.24);
            }

            .runev-pay-panel span {
                display: block;
                color: #cbd5e1;
                font-size: 0.82rem;
                font-weight: 850;
                margin-bottom: 0.45rem;
            }

            .runev-pay-panel strong {
                display: block;
                color: var(--runev-text);
                font-size: clamp(2rem, 4vw, 2.65rem);
                line-height: 1;
                font-weight: 900;
            }

            .runev-pay-panel p {
                margin: 0.55rem 0 0;
                color: #94a3b8;
                font-size: 0.9rem;
                font-weight: 700;
                overflow-wrap: anywhere;
            }

            .runev-payment-card-grid {
                margin-bottom: 0.7rem;
            }

            .runev-payment-option {
                min-height: 132px;
                display: flex;
                justify-content: space-between;
                gap: 0.8rem;
                padding: 1rem;
                margin-bottom: 0.55rem;
                border-radius: 18px;
                border: 1px solid rgba(148, 163, 184, 0.18);
                background: linear-gradient(145deg, rgba(30, 41, 59, 0.86), rgba(15, 23, 42, 0.68));
                box-shadow: 0 18px 45px rgba(2, 6, 23, 0.24);
                transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
            }

            .runev-payment-option:hover,
            .runev-payment-option.selected {
                transform: translateY(-2px) scale(1.01);
                border-color: rgba(0, 229, 168, 0.58);
                box-shadow: 0 22px 58px rgba(0, 229, 168, 0.16);
            }

            .runev-payment-option span {
                color: var(--runev-green);
                font-size: 0.75rem;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }

            .runev-payment-option strong {
                display: block;
                color: var(--runev-text);
                font-size: 1.2rem;
                font-weight: 900;
                margin-top: 0.35rem;
            }

            .runev-payment-option p {
                color: #cbd5e1;
                margin: 0.35rem 0 0;
                font-weight: 700;
            }

            .runev-payment-option b {
                align-self: flex-start;
                color: #03111f;
                background: var(--runev-green);
                border-radius: 999px;
                padding: 0.28rem 0.6rem;
                font-size: 0.72rem;
                white-space: nowrap;
            }

            .runev-upi-shell {
                margin: 0.9rem 0 0.75rem;
                padding: 1rem;
                border: 1px solid rgba(0, 229, 168, 0.22);
                border-radius: 24px;
                background:
                    linear-gradient(135deg, rgba(0, 229, 168, 0.10), rgba(59, 130, 246, 0.12)),
                    rgba(15, 23, 42, 0.74);
                box-shadow: 0 22px 62px rgba(2, 6, 23, 0.28);
                backdrop-filter: blur(18px);
            }

            .runev-upi-heading {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.9rem;
            }

            .runev-upi-heading span {
                display: block;
                color: var(--runev-green);
                font-size: 0.72rem;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }

            .runev-upi-heading strong {
                display: block;
                margin-top: 0.22rem;
                color: var(--runev-text);
                font-size: 1.05rem;
                font-weight: 900;
            }

            .runev-upi-heading b {
                color: #03111f;
                background: linear-gradient(135deg, var(--runev-green), #7dd3fc);
                border-radius: 999px;
                padding: 0.36rem 0.7rem;
                font-size: 0.72rem;
                font-weight: 950;
                white-space: nowrap;
            }

            .runev-upi-app-card {
                position: relative;
                min-height: 138px;
                overflow: hidden;
                padding: 1rem;
                margin-bottom: 0.45rem;
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 20px;
                background:
                    linear-gradient(145deg, rgba(30, 41, 59, 0.88), rgba(15, 23, 42, 0.78)),
                    rgba(30, 41, 59, 0.8);
                box-shadow: 0 18px 44px rgba(2, 6, 23, 0.28);
                backdrop-filter: blur(16px);
                transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
                animation: runevRise 260ms ease both;
            }

            .runev-upi-app-card::before {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(135deg, rgba(0, 229, 168, 0.16), rgba(59, 130, 246, 0.12));
                opacity: 0;
                transition: opacity 180ms ease;
            }

            .runev-upi-app-card:hover,
            .runev-upi-app-card.selected {
                transform: translateY(-3px);
                border-color: rgba(0, 229, 168, 0.72);
                box-shadow: 0 24px 70px rgba(0, 229, 168, 0.18), 0 0 0 1px rgba(59, 130, 246, 0.16) inset;
            }

            .runev-upi-app-card:hover::before,
            .runev-upi-app-card.selected::before {
                opacity: 1;
            }

            .runev-upi-app-card > * {
                position: relative;
                z-index: 1;
            }

            .runev-upi-app-top {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.75rem;
                margin-bottom: 0.85rem;
            }

            .runev-upi-logo {
                width: 3.25rem;
                height: 3.25rem;
                display: grid;
                place-items: center;
                border-radius: 18px;
                color: #03111f;
                background: #f8fafc;
                font-weight: 950;
                box-shadow: 0 12px 28px rgba(2, 6, 23, 0.28);
            }

            .runev-upi-logo.gpay { color: #1a73e8; background: linear-gradient(135deg, #ffffff, #e0f2fe); }
            .runev-upi-logo.phonepe { color: #ffffff; background: linear-gradient(135deg, #6739b7, #8b5cf6); }
            .runev-upi-logo.paytm { color: #ffffff; background: linear-gradient(135deg, #00baf2, #002e6e); }
            .runev-upi-logo.bhim { color: #ffffff; background: linear-gradient(135deg, #f97316, #16a34a); }
            .runev-upi-logo.other { color: #03111f; background: linear-gradient(135deg, var(--runev-green), #93c5fd); font-size: 0.86rem; }

            .runev-upi-check {
                width: 1.8rem;
                height: 1.8rem;
                display: grid;
                place-items: center;
                border-radius: 999px;
                color: #03111f;
                background: var(--runev-green);
                font-size: 0.92rem;
                font-weight: 950;
                box-shadow: 0 0 0 8px rgba(0, 229, 168, 0.12);
            }

            .runev-upi-app-card:not(.selected) .runev-upi-check {
                background: rgba(148, 163, 184, 0.14);
                box-shadow: none;
            }

            .runev-upi-app-card strong {
                display: block;
                color: var(--runev-text);
                font-size: 1.08rem;
                font-weight: 950;
            }

            .runev-upi-app-card span {
                display: block;
                margin-top: 0.25rem;
                color: #cbd5e1;
                font-size: 0.86rem;
                font-weight: 750;
            }

            .runev-upi-selected {
                display: flex;
                align-items: center;
                gap: 0.55rem;
                margin: 0.65rem 0 0.9rem;
                padding: 0.85rem 0.95rem;
                border: 1px solid rgba(0, 229, 168, 0.26);
                border-radius: 18px;
                background: rgba(30, 41, 59, 0.72);
                box-shadow: 0 14px 34px rgba(2, 6, 23, 0.18);
            }

            .runev-upi-selected.muted {
                border-color: rgba(148, 163, 184, 0.18);
            }

            .runev-upi-selected-dot {
                width: 0.72rem;
                height: 0.72rem;
                border-radius: 999px;
                background: var(--runev-green);
                box-shadow: 0 0 0 7px rgba(0, 229, 168, 0.12);
            }

            .runev-upi-selected.muted .runev-upi-selected-dot {
                background: #64748b;
                box-shadow: 0 0 0 7px rgba(100, 116, 139, 0.12);
            }

            .runev-upi-selected span {
                color: #cbd5e1;
                font-size: 0.82rem;
                font-weight: 800;
            }

            .runev-upi-selected strong {
                color: var(--runev-text);
                font-weight: 950;
            }

            .runev-manual-upi-card {
                display: grid;
                grid-template-columns: minmax(0, 0.9fr) minmax(260px, 1.1fr);
                align-items: center;
                gap: 1.1rem;
                margin: 0.75rem 0 0.9rem;
                padding: 1.05rem;
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: 18px;
                background:
                    linear-gradient(145deg, rgba(0, 229, 168, 0.08), rgba(59, 130, 246, 0.07)),
                    rgba(15, 23, 42, 0.72);
                box-shadow: 0 16px 44px rgba(2, 6, 23, 0.22);
            }

            .runev-manual-upi-card > div:first-child span {
                display: block;
                color: var(--runev-green);
                font-size: 0.76rem;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }

            .runev-manual-upi-card > div:first-child strong {
                display: block;
                margin-top: 0.35rem;
                color: var(--runev-text);
                font-size: 1.2rem;
                font-weight: 900;
            }

            .runev-manual-upi-card > div:first-child p {
                margin: 0.45rem 0 0;
                color: #cbd5e1;
                font-weight: 700;
                line-height: 1.5;
            }

            .runev-disabled-pay {
                margin-top: 0.75rem;
            }

            .runev-disabled-pay button {
                width: 100%;
                min-height: 56px;
                border: 1px solid rgba(148, 163, 184, 0.14);
                border-radius: 999px;
                background: #334155;
                color: #94a3b8;
                font-size: 1.05rem;
                font-weight: 900;
            }

            .runev-disabled-pay span {
                display: block;
                margin-top: 0.55rem;
                color: #94a3b8;
                font-size: 0.9rem;
                font-weight: 700;
                text-align: center;
            }

            .runev-secure-note,
            .runev-upi-qr {
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 0.9rem;
                margin: 0;
                border-radius: 16px;
                border: 1px solid rgba(148, 163, 184, 0.14);
                background: rgba(15, 23, 42, 0.58);
            }

            .runev-lock {
                width: 3rem;
                height: 3rem;
                display: grid;
                place-items: center;
                border-radius: 16px;
                color: #03111f;
                font-size: 0.72rem;
                font-weight: 900;
                background: var(--runev-green);
            }

            .runev-secure-note strong {
                display: block;
                color: var(--runev-text);
                font-weight: 900;
            }

            .runev-secure-note span {
                display: block;
                color: #cbd5e1;
                font-weight: 700;
                margin-top: 0.2rem;
            }

            .runev-trust-badges {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                margin-top: 0.65rem;
            }

            .runev-trust-badges b {
                color: #dbeafe;
                background: rgba(59, 130, 246, 0.14);
                border: 1px solid rgba(59, 130, 246, 0.22);
                border-radius: 999px;
                padding: 0.25rem 0.55rem;
                font-size: 0.72rem;
                font-weight: 850;
            }

            .runev-qr-grid {
                flex: 0 0 auto;
                display: grid;
                grid-template-columns: repeat(10, 8px);
                grid-template-rows: repeat(10, 8px);
                gap: 3px;
                padding: 11px;
                background: #f8fafc;
                border-radius: 12px;
                border: 5px solid #e2e8f0;
                box-shadow: 0 12px 28px rgba(2, 6, 23, 0.24);
            }

            .runev-qr-grid i {
                display: block;
                background: #f8fafc;
                border-radius: 2px;
            }

            .runev-qr-grid i.on {
                background: #0f172a;
            }

            .runev-success-screen {
                text-align: center;
                max-width: 720px;
                margin: 2rem auto;
                padding: 2rem;
                border: 1px solid rgba(0, 229, 168, 0.32);
                border-radius: 26px;
                background: linear-gradient(145deg, rgba(0, 229, 168, 0.16), rgba(30, 41, 59, 0.82));
                box-shadow: var(--runev-shadow);
            }

            .runev-success-check {
                width: 5rem;
                height: 5rem;
                display: grid;
                place-items: center;
                margin: 0 auto 1rem;
                border-radius: 999px;
                color: #03111f;
                background: var(--runev-green);
                font-size: 2.4rem;
                font-weight: 950;
                box-shadow: 0 0 0 12px rgba(0, 229, 168, 0.12);
                animation: runevPulse 1.4s ease infinite;
            }

            .runev-success-screen h1 {
                margin: 0.3rem 0;
                font-size: clamp(2.4rem, 6vw, 4.4rem);
            }

            .runev-success-screen p {
                color: #cbd5e1;
                font-size: 1.05rem;
            }

            .runev-success-meta {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.7rem;
                margin-top: 1rem;
                text-align: left;
            }

            .runev-success-meta span,
            .runev-success-meta strong {
                padding: 0.8rem;
                border-radius: 14px;
                background: rgba(15, 23, 42, 0.52);
                overflow-wrap: anywhere;
            }

            .runev-skeleton {
                min-height: 104px;
                border-radius: 18px;
                background: linear-gradient(90deg, rgba(30, 41, 59, 0.55), rgba(51, 65, 85, 0.85), rgba(30, 41, 59, 0.55));
                background-size: 220% 100%;
                animation: runevShimmer 1.4s infinite linear;
            }

            .folium-map {
                border-radius: 18px;
                border: 1px solid var(--runev-border);
                box-shadow: var(--runev-shadow);
            }

            @media (max-width: 1100px) {
                .runev-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
                .runev-two-col { grid-template-columns: 1fr; }
                .runev-trip { grid-template-columns: 1fr; }
            }

            @media (max-width: 680px) {
                .block-container { padding: 0.8rem 0.8rem 2rem; }
                .runev-hero { align-items: flex-start; flex-direction: column; border-radius: 16px; }
                
                .block-container:has(.runev-auth-page) {
                    height: 100vh;
                    padding: 0;
                    overflow-y: auto;
                    justify-content: flex-start;
                    padding-top: 2rem;
                }
                
                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] {
                    max-width: 100%;
                    padding: 0 1rem;
                }
                
                .block-container:has(.runev-auth-page) [data-testid="column"]:has(.runev-auth-card-copy),
                .block-container:has(.runev-auth-page) [data-testid="column"]:nth-of-type(2) {
                    max-width: 100%;
                    padding: 1.5rem;
                    border-radius: 14px;
                    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
                }
                
                .runev-auth-card-copy h2 {
                    font-size: 1.35rem;
                }
                
                .runev-auth-card-copy p {
                    font-size: 0.9rem;
                }
                
                .block-container:has(.runev-auth-page) .stTextInput input {
                    min-height: 2.6rem;
                    font-size: 0.9rem;
                }
                
                .block-container:has(.runev-auth-page) .stButton > button,
                .block-container:has(.runev-auth-page) .stFormSubmitButton > button,
                .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > button {
                    min-height: 2.6rem;
                    font-size: 0.9rem;
                }
                
                .block-container:has(.runev-driver-auth-page) {
                    height: 100vh;
                    padding: 0;
                    overflow-y: auto;
                    justify-content: flex-start;
                    padding-top: 2rem;
                }
                
                .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                    max-width: 100%;
                    padding: 0 1rem;
                }
                
                .block-container:has(.runev-driver-auth-page) [data-testid="column"]:has(.runev-driver-auth-copy),
                .block-container:has(.runev-driver-auth-page) [data-testid="column"]:nth-of-type(2) {
                    max-width: 100%;
                    padding: 1.5rem;
                    border-radius: 14px;
                    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
                }
                
                .runev-driver-auth-copy h2 {
                    font-size: 1.35rem;
                }
                
                .runev-driver-auth-copy p {
                    font-size: 0.9rem;
                }
                
                .block-container:has(.runev-driver-auth-page) .stTextInput input {
                    min-height: 2.6rem;
                    font-size: 0.9rem;
                }
                
                .block-container:has(.runev-driver-auth-page) .stButton > button,
                .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button,
                .block-container:has(.runev-driver-auth-page) [data-testid="stLinkButton"] > button {
                    min-height: 2.6rem;
                    font-size: 0.9rem;
                }
                
                .runev-auth-visual {
                    display: none;
                }
                
                .runev-driver-auth-visual {
                    display: none;
                }
                
                .runev-fleet-preview-grid {
                    grid-template-columns: 1fr;
                }
                .runev-driver-activity div {
                    grid-template-columns: auto minmax(0, 1fr);
                }
                .runev-driver-activity strong {
                    grid-column: 2;
                }
                .runev-kpi-grid { grid-template-columns: 1fr; }
                .runev-driver-top,
                .runev-driver-grid,
                .runev-summary-grid,
                .runev-success-meta {
                    grid-template-columns: 1fr;
                }
                .runev-summary-line,
                .runev-upi-qr,
                .runev-secure-note,
                .runev-upi-heading,
                .runev-upi-selected {
                    align-items: flex-start;
                    flex-direction: column;
                }
                .runev-manual-upi-card {
                    grid-template-columns: 1fr;
                }
                .runev-timeline {
                    display: grid;
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }
                .runev-timeline-line {
                    display: none;
                }
                .runev-step {
                    align-items: flex-start;
                    text-align: left;
                    max-width: none;
                }
            }

            @keyframes runevRise {
                from { opacity: 0; transform: translateY(8px); }
                to { opacity: 1; transform: translateY(0); }
            }

            @keyframes runevFade {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes runevShimmer {
                0% { background-position: 220% 0; }
                100% { background-position: -220% 0; }
            }

            @keyframes runevNotify {
                0% { opacity: 0; transform: translateY(-10px); }
                8% { opacity: 1; transform: translateY(0); }
                78% { opacity: 1; transform: translateY(0); }
                100% { opacity: 0; transform: translateY(-10px); visibility: hidden; }
            }

            @keyframes runevPulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.04); }
            }

            :root,
            html[data-runev-theme="dark"] {
                color-scheme: dark;
                --runev-bg: #0b1220;
                --runev-panel: #111827;
                --runev-surface: #111827;
                --runev-surface-secondary: #172033;
                --runev-card: #1e293b;
                --runev-card-soft: rgba(30, 41, 59, 0.78);
                --runev-border: rgba(148, 163, 184, 0.22);
                --runev-divider: rgba(148, 163, 184, 0.16);
                --runev-text: #f8fafc;
                --runev-text-secondary: #cbd5e1;
                --runev-muted: #94a3b8;
                --runev-green: #14e6b0;
                --runev-accent: #14e6b0;
                --runev-success: #10b981;
                --runev-warn: #f59e0b;
                --runev-danger: #ef4444;
                --runev-info: #3b82f6;
                --runev-gradient-start: #14e6b0;
                --runev-gradient-end: #6366f1;
                --runev-radius-sm: 8px;
                --runev-radius-md: 12px;
                --runev-radius-lg: 18px;
                --runev-radius-xl: 24px;
                --runev-shadow-soft: 0 10px 26px rgba(2, 6, 23, 0.18);
                --runev-shadow-medium: 0 18px 46px rgba(2, 6, 23, 0.28);
                --runev-shadow: 0 24px 70px rgba(2, 6, 23, 0.34);
            }

            html[data-runev-theme="light"] {
                color-scheme: light;
                --runev-bg: #f6f8fb;
                --runev-panel: #ffffff;
                --runev-surface: #ffffff;
                --runev-surface-secondary: #eef3f8;
                --runev-card: #ffffff;
                --runev-card-soft: rgba(255, 255, 255, 0.94);
                --runev-border: rgba(15, 23, 42, 0.14);
                --runev-divider: rgba(15, 23, 42, 0.10);
                --runev-text: #0f172a;
                --runev-text-secondary: #334155;
                --runev-muted: #64748b;
                --runev-green: #059669;
                --runev-accent: #059669;
                --runev-success: #059669;
                --runev-warn: #b45309;
                --runev-danger: #dc2626;
                --runev-info: #2563eb;
                --runev-gradient-start: #10b981;
                --runev-gradient-end: #2563eb;
                --runev-shadow-soft: 0 10px 24px rgba(15, 23, 42, 0.08);
                --runev-shadow-medium: 0 18px 42px rgba(15, 23, 42, 0.12);
                --runev-shadow: 0 24px 60px rgba(15, 23, 42, 0.14);
            }

            html[data-runev-theme="system"] {
                color-scheme: light dark;
            }

            @media (prefers-color-scheme: light) {
                html[data-runev-theme="system"] {
                    --runev-bg: #f6f8fb;
                    --runev-panel: #ffffff;
                    --runev-surface: #ffffff;
                    --runev-surface-secondary: #eef3f8;
                    --runev-card: #ffffff;
                    --runev-card-soft: rgba(255, 255, 255, 0.94);
                    --runev-border: rgba(15, 23, 42, 0.14);
                    --runev-divider: rgba(15, 23, 42, 0.10);
                    --runev-text: #0f172a;
                    --runev-text-secondary: #334155;
                    --runev-muted: #64748b;
                    --runev-green: #059669;
                    --runev-accent: #059669;
                    --runev-success: #059669;
                    --runev-warn: #b45309;
                    --runev-danger: #dc2626;
                    --runev-info: #2563eb;
                    --runev-gradient-start: #10b981;
                    --runev-gradient-end: #2563eb;
                    --runev-shadow-soft: 0 10px 24px rgba(15, 23, 42, 0.08);
                    --runev-shadow-medium: 0 18px 42px rgba(15, 23, 42, 0.12);
                    --runev-shadow: 0 24px 60px rgba(15, 23, 42, 0.14);
                }
            }

            body, .stApp {
                background:
                    linear-gradient(135deg, color-mix(in srgb, var(--runev-bg) 94%, var(--runev-gradient-start) 6%), var(--runev-bg)),
                    var(--runev-bg) !important;
                color: var(--runev-text) !important;
            }

            h1, h2, h3,
            [data-testid="stMarkdownContainer"],
            [data-testid="stMarkdownContainer"] p,
            [data-testid="stMarkdownContainer"] span,
            label, .stTextInput label, .stTextArea label, .stSelectbox label {
                color: var(--runev-text) !important;
            }

            .stCaptionContainer,
            .stCaptionContainer *,
            .runev-subtitle {
                color: var(--runev-text-secondary) !important;
            }

            .runev-card, div[data-testid="stExpander"], div[data-testid="stMetric"] {
                background: var(--runev-card-soft) !important;
                border-color: var(--runev-border) !important;
                box-shadow: var(--runev-shadow-soft) !important;
            }

            .runev-hero,
            .runev-auth-visual,
            .runev-driver-auth-visual,
            .block-container:has(.runev-auth-page) [data-testid="column"]:has(.runev-auth-card-copy),
            .block-container:has(.runev-driver-auth-page) [data-testid="column"]:has(.runev-driver-auth-copy) {
                background:
                    linear-gradient(145deg, color-mix(in srgb, var(--runev-surface) 88%, var(--runev-gradient-start) 12%), var(--runev-surface)) !important;
                border-color: var(--runev-border) !important;
                box-shadow: var(--runev-shadow-medium) !important;
            }

            .stTextInput input,
            .stNumberInput input,
            .stTextArea textarea,
            .stSelectbox div[data-baseweb="select"] > div {
                background: var(--runev-surface) !important;
                border-color: var(--runev-border) !important;
                color: var(--runev-text) !important;
                -webkit-text-fill-color: var(--runev-text) !important;
            }

            .stButton > button,
            .stFormSubmitButton > button,
            div[data-testid="stDownloadButton"] > button {
                background: linear-gradient(135deg, var(--runev-gradient-start), var(--runev-gradient-end)) !important;
                border-color: color-mix(in srgb, var(--runev-accent) 58%, transparent) !important;
                color: #ffffff !important;
            }

            .stButton > button:focus-visible,
            .stFormSubmitButton > button:focus-visible,
            input:focus-visible,
            textarea:focus-visible {
                outline: 3px solid color-mix(in srgb, var(--runev-accent) 45%, transparent) !important;
                outline-offset: 2px !important;
            }

            [data-testid="stSidebar"] {
                background: var(--runev-surface) !important;
                border-right-color: var(--runev-border) !important;
            }

            /* Premium RunEV visual system overrides. These keep Streamlit logic intact and
               tune layout density, contrast, and responsiveness across both apps. */
            :root,
            html[data-runev-theme="dark"] {
                --runev-bg: #0a1020;
                --runev-panel: #111827;
                --runev-surface: #121b2c;
                --runev-surface-secondary: #18243a;
                --runev-card: #172033;
                --runev-card-soft: rgba(18, 27, 44, 0.88);
                --runev-border: rgba(148, 163, 184, 0.20);
                --runev-divider: rgba(148, 163, 184, 0.14);
                --runev-text: #f8fafc;
                --runev-text-secondary: #cbd5e1;
                --runev-muted: #94a3b8;
                --runev-green: #12e6b4;
                --runev-accent: #12e6b4;
                --runev-gradient-start: #11d8b0;
                --runev-gradient-end: #6d7df6;
                --runev-shadow-soft: 0 14px 38px rgba(2, 6, 23, 0.22);
                --runev-shadow-medium: 0 22px 58px rgba(2, 6, 23, 0.30);
                --runev-shadow: 0 28px 86px rgba(2, 6, 23, 0.38);
            }

            html[data-runev-theme="light"] {
                --runev-bg: #f4f7fb;
                --runev-panel: #ffffff;
                --runev-surface: #ffffff;
                --runev-surface-secondary: #edf3f8;
                --runev-card: #ffffff;
                --runev-card-soft: rgba(255, 255, 255, 0.96);
                --runev-border: rgba(15, 23, 42, 0.12);
                --runev-divider: rgba(15, 23, 42, 0.09);
                --runev-text: #0f172a;
                --runev-text-secondary: #334155;
                --runev-muted: #64748b;
                --runev-green: #047857;
                --runev-accent: #047857;
                --runev-gradient-start: #10b981;
                --runev-gradient-end: #4f46e5;
                --runev-shadow-soft: 0 12px 28px rgba(15, 23, 42, 0.08);
                --runev-shadow-medium: 0 20px 48px rgba(15, 23, 42, 0.12);
                --runev-shadow: 0 28px 70px rgba(15, 23, 42, 0.15);
            }

            body,
            .stApp {
                min-height: 100svh;
                background:
                    radial-gradient(circle at 10% 0%, color-mix(in srgb, var(--runev-gradient-start) 18%, transparent), transparent 29rem),
                    radial-gradient(circle at 88% 8%, rgba(99, 102, 241, 0.16), transparent 25rem),
                    linear-gradient(135deg, color-mix(in srgb, var(--runev-bg) 94%, #1f2937 6%), var(--runev-bg)) !important;
            }

            .block-container {
                max-width: min(1320px, 100%) !important;
                padding: clamp(0.75rem, 1.4vw, 1.15rem) clamp(1rem, 2vw, 1.75rem) 2rem !important;
            }

            .block-container > div:first-child {
                padding-top: 0 !important;
            }

            .block-container:has(.runev-auth-page),
            .block-container:has(.runev-driver-auth-page) {
                min-height: 100svh !important;
                height: auto !important;
                justify-content: center !important;
                padding: clamp(0.9rem, 1.6vw, 1.25rem) !important;
                overflow: auto !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stVerticalBlock"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stVerticalBlock"] {
                gap: clamp(0.8rem, 1.5vw, 1.15rem) !important;
            }

            .runev-auth-heading,
            .runev-driver-auth-heading {
                width: min(100%, 1220px);
                margin: 0 auto clamp(0.75rem, 1.4vw, 1rem);
                padding: clamp(1.45rem, 3vw, 2.35rem);
                border: 1px solid var(--runev-border);
                border-radius: 28px;
                background:
                    linear-gradient(115deg, color-mix(in srgb, var(--runev-gradient-start) 18%, transparent), transparent 34%),
                    linear-gradient(135deg, color-mix(in srgb, var(--runev-surface) 88%, var(--runev-bg) 12%), color-mix(in srgb, var(--runev-surface-secondary) 78%, var(--runev-bg) 22%));
                box-shadow: var(--runev-shadow-medium);
            }

            .runev-auth-heading span,
            .runev-driver-auth-heading span,
            .runev-auth-card-copy span,
            .runev-driver-auth-copy span {
                color: var(--runev-accent) !important;
                font-size: 0.76rem;
                font-weight: 850;
                letter-spacing: 0.12em;
                text-transform: uppercase;
            }

            .runev-auth-heading h1,
            .runev-driver-auth-heading h1 {
                max-width: 980px;
                margin: 0.55rem 0 0;
                font-size: clamp(2.1rem, 4.2vw, 4.1rem);
                line-height: 0.96;
                font-weight: 850;
            }

            .runev-auth-heading p,
            .runev-driver-auth-heading p {
                max-width: 860px;
                margin: 0.75rem 0 0;
                color: var(--runev-text-secondary) !important;
                font-size: clamp(1rem, 1.5vw, 1.2rem);
                line-height: 1.5;
                font-weight: 650;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                width: min(100%, 1220px) !important;
                max-width: 1220px !important;
                padding: 0 !important;
                gap: clamp(1rem, 2vw, 1.5rem) !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="column"]:has(.runev-auth-card-copy),
            .block-container:has(.runev-driver-auth-page) [data-testid="column"]:has(.runev-driver-auth-copy) {
                padding: clamp(1.15rem, 2vw, 1.65rem) !important;
                border-radius: 20px !important;
                background: var(--runev-card-soft) !important;
                border: 1px solid var(--runev-border) !important;
                box-shadow: var(--runev-shadow-soft) !important;
                backdrop-filter: blur(18px);
            }

            .block-container:has(.runev-auth-page) [data-testid="column"]:nth-of-type(2),
            .block-container:has(.runev-driver-auth-page) [data-testid="column"]:nth-of-type(2) {
                padding: clamp(1.15rem, 2vw, 1.65rem) !important;
                border-radius: 20px !important;
                background: var(--runev-card-soft) !important;
                border: 1px solid var(--runev-border) !important;
                box-shadow: var(--runev-shadow-soft) !important;
            }

            .runev-auth-card-copy h2,
            .runev-driver-auth-copy h2 {
                margin: 0.35rem 0 0.35rem;
                font-size: clamp(1.25rem, 1.8vw, 1.6rem);
                line-height: 1.05;
            }

            .runev-auth-card-copy p,
            .runev-driver-auth-copy p,
            .runev-auth-legal {
                color: var(--runev-text-secondary) !important;
                line-height: 1.45;
            }

            .runev-auth-visual,
            .runev-driver-auth-visual {
                min-height: clamp(360px, 48vh, 520px);
                height: 100%;
                padding: clamp(1.4rem, 2.6vw, 2.1rem) !important;
                border-radius: 20px !important;
                background:
                    linear-gradient(145deg, color-mix(in srgb, var(--runev-surface-secondary) 82%, var(--runev-gradient-end) 18%), var(--runev-surface)) !important;
                border: 1px solid var(--runev-border) !important;
                box-shadow: var(--runev-shadow-medium) !important;
                overflow: hidden;
                position: relative;
            }

            .runev-auth-visual::after,
            .runev-driver-auth-visual::after {
                content: "";
                position: absolute;
                inset: auto 1.25rem 1.25rem auto;
                width: 8rem;
                aspect-ratio: 1;
                border-radius: 999px;
                background: linear-gradient(135deg, var(--runev-gradient-start), var(--runev-gradient-end));
                opacity: 0.18;
                filter: blur(18px);
                pointer-events: none;
            }

            .runev-auth-visual h2,
            .runev-driver-auth-visual h2 {
                margin: clamp(1.25rem, 2vw, 1.8rem) 0 0.85rem;
                font-size: clamp(2rem, 3.4vw, 3.15rem);
                line-height: 1.08;
                font-weight: 850;
            }

            .runev-auth-visual p,
            .runev-driver-auth-visual p {
                max-width: 780px;
                color: var(--runev-text-secondary) !important;
                font-size: clamp(1rem, 1.45vw, 1.18rem);
                line-height: 1.65;
                font-weight: 620;
            }

            .runev-auth-preview-grid,
            .runev-fleet-preview-grid,
            .runev-driver-activity {
                position: relative;
                z-index: 1;
            }

            .runev-auth-preview-grid > div,
            .runev-fleet-preview-grid > div,
            .runev-driver-activity > div {
                background: color-mix(in srgb, var(--runev-surface) 78%, transparent) !important;
                border: 1px solid var(--runev-border) !important;
                box-shadow: var(--runev-shadow-soft);
            }

            .runev-hero {
                min-height: auto;
                padding: clamp(1rem, 1.9vw, 1.55rem) clamp(1.1rem, 2vw, 1.8rem) !important;
                margin-bottom: clamp(0.85rem, 1.5vw, 1.2rem) !important;
                border-radius: 24px !important;
                background:
                    linear-gradient(115deg, color-mix(in srgb, var(--runev-gradient-start) 15%, transparent), transparent 42%),
                    linear-gradient(145deg, color-mix(in srgb, var(--runev-surface-secondary) 78%, var(--runev-bg) 22%), var(--runev-surface)) !important;
            }

            .runev-title {
                font-size: clamp(1.75rem, 3vw, 3.1rem) !important;
                line-height: 1 !important;
                font-weight: 850 !important;
            }

            .runev-subtitle {
                max-width: 900px;
                margin-top: 0.45rem !important;
                font-size: clamp(0.96rem, 1.1vw, 1.08rem);
                line-height: 1.45;
            }

            .runev-card,
            div[data-testid="stExpander"],
            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 18px !important;
                background: var(--runev-card-soft) !important;
                border: 1px solid var(--runev-border) !important;
                box-shadow: var(--runev-shadow-soft) !important;
            }

            .runev-card {
                padding: clamp(0.85rem, 1.25vw, 1.1rem) !important;
            }

            .runev-metric {
                min-height: 118px;
                display: grid;
                align-content: space-between;
                gap: 0.2rem;
            }

            .runev-metric-icon {
                width: 2.25rem;
                height: 2.25rem;
                border-radius: 12px;
                display: inline-grid;
                place-items: center;
                background: color-mix(in srgb, var(--runev-accent) 16%, transparent);
                color: var(--runev-accent) !important;
                font-size: 1.05rem;
                font-weight: 850;
            }

            .runev-metric-label {
                color: var(--runev-text-secondary) !important;
                font-size: 0.76rem !important;
                font-weight: 780 !important;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }

            .runev-metric-value {
                font-size: clamp(1.35rem, 1.9vw, 2rem) !important;
                line-height: 1 !important;
                font-weight: 850 !important;
            }

            .runev-metric-delta {
                color: var(--runev-muted) !important;
                font-size: 0.82rem !important;
            }

            [data-testid="stMetric"] {
                padding: 0.85rem 0.95rem !important;
                border-radius: 16px !important;
                background: var(--runev-card-soft) !important;
                border: 1px solid var(--runev-border) !important;
                box-shadow: var(--runev-shadow-soft) !important;
            }

            .stButton > button,
            .stFormSubmitButton > button,
            [data-testid="stLinkButton"] > a,
            div[data-testid="stDownloadButton"] > button {
                min-height: 2.65rem !important;
                border-radius: 14px !important;
                font-weight: 780 !important;
                box-shadow: 0 14px 32px color-mix(in srgb, var(--runev-gradient-start) 20%, transparent) !important;
            }

            .stButton > button:hover,
            .stFormSubmitButton > button:hover,
            [data-testid="stLinkButton"] > a:hover,
            div[data-testid="stDownloadButton"] > button:hover {
                transform: translateY(-1px);
                filter: brightness(1.04);
            }

            .stTextInput input,
            .stNumberInput input,
            .stTextArea textarea,
            .stSelectbox div[data-baseweb="select"] > div {
                min-height: 2.65rem !important;
                border-radius: 14px !important;
                background: color-mix(in srgb, var(--runev-surface) 88%, var(--runev-bg) 12%) !important;
                border: 1px solid var(--runev-border) !important;
                box-shadow: inset 0 1px 0 color-mix(in srgb, #ffffff 7%, transparent);
            }

            div[role="radiogroup"] label {
                min-height: 2.45rem !important;
                border-radius: 12px !important;
                background: color-mix(in srgb, var(--runev-surface) 76%, transparent) !important;
                border: 1px solid var(--runev-border) !important;
                box-shadow: none !important;
            }

            div[role="radiogroup"] label:has(input:checked) {
                background: color-mix(in srgb, var(--runev-accent) 13%, var(--runev-surface) 87%) !important;
                border-color: color-mix(in srgb, var(--runev-accent) 55%, transparent) !important;
            }

            [data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, color-mix(in srgb, var(--runev-surface) 92%, var(--runev-bg) 8%), var(--runev-surface)) !important;
                border-right: 1px solid var(--runev-border) !important;
            }

            .runev-sidebar-brand {
                padding: 0.8rem 0 1rem !important;
                margin-bottom: 0.75rem !important;
            }

            .runev-sidebar-logo {
                font-size: 1.35rem !important;
                letter-spacing: 0 !important;
            }

            [data-testid="stSidebar"] div[role="radiogroup"] label {
                width: 100%;
                border-radius: 14px !important;
                justify-content: flex-start;
            }

            .runev-badge {
                border-radius: 999px !important;
                font-weight: 850 !important;
                letter-spacing: 0.01em;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.18);
            }

            [data-testid="stAlert"] {
                border-radius: 16px !important;
                border: 1px solid var(--runev-border) !important;
                background: color-mix(in srgb, var(--runev-info) 14%, var(--runev-surface) 86%) !important;
            }

            iframe,
            [data-testid="stIFrame"] {
                border-radius: 18px !important;
            }

            @media (min-width: 1100px) {
                .block-container:not(:has(.runev-auth-page)):not(:has(.runev-driver-auth-page)) {
                    min-height: 100svh;
                }

                .block-container:has(.runev-auth-page) .stTabs [data-baseweb="tab-list"],
                .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] {
                    flex-wrap: nowrap !important;
                }
            }

            @media (max-width: 900px) {
                .block-container:has(.runev-auth-page),
                .block-container:has(.runev-driver-auth-page) {
                    overflow-y: auto !important;
                    justify-content: flex-start !important;
                }

                .runev-auth-heading,
                .runev-driver-auth-heading {
                    border-radius: 22px;
                    padding: 1.2rem;
                }

                .runev-auth-heading h1,
                .runev-driver-auth-heading h1 {
                    font-size: clamp(2rem, 9vw, 3rem);
                    line-height: 1.02;
                }

                .runev-auth-visual,
                .runev-driver-auth-visual {
                    min-height: auto;
                }

                .runev-auth-visual h2,
                .runev-driver-auth-visual h2 {
                    font-size: clamp(1.65rem, 7vw, 2.25rem);
                }

                .runev-hero {
                    align-items: flex-start;
                    flex-direction: column;
                }
            }

            @media (max-width: 640px) {
                .block-container {
                    padding: 0.75rem 0.75rem 1.5rem !important;
                }

                .block-container:has(.runev-auth-page),
                .block-container:has(.runev-driver-auth-page) {
                    padding: 0.75rem !important;
                }

                .runev-auth-heading,
                .runev-driver-auth-heading,
                .runev-hero {
                    border-radius: 18px !important;
                }

                .runev-metric {
                    min-height: 102px;
                }

                div[role="radiogroup"] {
                    gap: 0.4rem !important;
                }
            }

            /* Auth screens must match the deployed dark RunEV reference exactly:
               wide hero, two balanced columns, compact controls, no desktop clipping. */
            .stApp:has(.runev-auth-page),
            .stApp:has(.runev-driver-auth-page),
            body:has(.runev-auth-page),
            body:has(.runev-driver-auth-page) {
                background:
                    radial-gradient(circle at 12% 12%, rgba(0, 229, 168, 0.14), transparent 28rem),
                    linear-gradient(135deg, #0b1220 0%, #111827 52%, #172033 100%) !important;
                color: #f8fafc !important;
            }

            .block-container:has(.runev-auth-page),
            .block-container:has(.runev-driver-auth-page) {
                width: 100% !important;
                max-width: none !important;
                min-height: 100svh !important;
                height: auto !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: flex-start !important;
                align-items: stretch !important;
                padding: clamp(1rem, 2vw, 2.35rem) clamp(1rem, 2vw, 2.35rem) 0.75rem !important;
                overflow: auto !important;
                box-sizing: border-box !important;
            }

            .block-container:has(.runev-auth-page) > div,
            .block-container:has(.runev-driver-auth-page) > div {
                width: 100% !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stVerticalBlock"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stVerticalBlock"] {
                gap: 0.8rem !important;
            }

            .runev-auth-heading,
            .runev-driver-auth-heading {
                width: 100% !important;
                max-width: none !important;
                min-height: clamp(128px, 20vh, 205px) !important;
                margin: 0 0 clamp(0.9rem, 2vh, 1.55rem) !important;
                padding: clamp(1.35rem, 2.4vw, 2.35rem) !important;
                border-radius: 30px !important;
                border: 1px solid rgba(148, 163, 184, 0.22) !important;
                background:
                    linear-gradient(90deg, rgba(0, 229, 168, 0.18), rgba(59, 130, 246, 0.08) 47%, rgba(255, 255, 255, 0.03)),
                    rgba(30, 41, 59, 0.86) !important;
                box-shadow: 0 28px 86px rgba(2, 6, 23, 0.34) !important;
            }

            .runev-auth-heading h1,
            .runev-driver-auth-heading h1 {
                margin-top: 0.65rem !important;
                max-width: 1120px !important;
                color: #f8fafc !important;
                font-size: clamp(2.35rem, 3.2vw, 3.45rem) !important;
                line-height: 1.02 !important;
                font-weight: 850 !important;
            }

            .runev-auth-heading p,
            .runev-driver-auth-heading p {
                max-width: 1120px !important;
                margin-top: 0.65rem !important;
                color: #cbd5e1 !important;
                font-size: clamp(1rem, 1.3vw, 1.18rem) !important;
                line-height: 1.45 !important;
            }

            .runev-auth-heading span,
            .runev-driver-auth-heading span,
            .runev-auth-card-copy span,
            .runev-driver-auth-copy span {
                color: #14e6b0 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                width: 100% !important;
                max-width: none !important;
                height: auto !important;
                min-height: 0 !important;
                align-items: stretch !important;
                gap: clamp(1rem, 1.35vw, 1.55rem) !important;
                padding: 0 !important;
                margin: 0 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child,
            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child,
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child,
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child {
                display: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"] {
                flex: 1 1 0 !important;
                width: 50% !important;
                min-width: 0 !important;
                padding: 0 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="column"]:has(.runev-auth-card-copy),
            .block-container:has(.runev-driver-auth-page) [data-testid="column"]:has(.runev-driver-auth-copy) {
                height: 100% !important;
                padding: 0 !important;
                background: transparent !important;
                border: 0 !important;
                box-shadow: none !important;
                overflow: visible !important;
            }

            .runev-auth-card-copy,
            .runev-driver-auth-copy {
                margin: 0 0 0.9rem !important;
                padding: 0 !important;
                background: transparent !important;
                border: 0 !important;
                box-shadow: none !important;
            }

            .runev-auth-card-copy h2,
            .runev-driver-auth-copy h2 {
                color: #f8fafc !important;
                font-size: 1.02rem !important;
                line-height: 1.25 !important;
                letter-spacing: 0.1em !important;
                text-transform: uppercase !important;
                margin: 2.1rem 0 6.2rem !important;
            }

            .runev-auth-card-copy p,
            .runev-driver-auth-copy p {
                max-width: 760px !important;
                color: #cbd5e1 !important;
                font-size: clamp(1.02rem, 1.25vw, 1.18rem) !important;
                line-height: 1.5 !important;
                font-weight: 650 !important;
                margin: 0 0 1.35rem !important;
            }

            .block-container:has(.runev-auth-page) .stTabs,
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] {
                margin-top: 0.75rem !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"],
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] {
                display: flex !important;
                flex-wrap: nowrap !important;
                gap: 1.35rem !important;
                border-bottom: 1px solid rgba(148, 163, 184, 0.14) !important;
                overflow: hidden !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button,
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label {
                width: auto !important;
                min-width: max-content !important;
                min-height: 2.35rem !important;
                padding: 0.4rem 0 !important;
                border: 0 !important;
                border-radius: 0 !important;
                background: transparent !important;
                color: #f8fafc !important;
                box-shadow: none !important;
                font-size: 1rem !important;
                font-weight: 750 !important;
                line-height: 1.2 !important;
                white-space: nowrap !important;
            }

            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label > div:first-child {
                display: none !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button[aria-selected="true"],
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label:has(input:checked) {
                border-bottom: 3px solid #ff3b5f !important;
                color: #ffffff !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [data-baseweb="tab-panel"],
            .block-container:has(.runev-driver-auth-page) form,
            .block-container:has(.runev-auth-page) form {
                border: 1px solid rgba(148, 163, 184, 0.13) !important;
                border-radius: 12px !important;
                background: rgba(15, 23, 42, 0.20) !important;
                padding: clamp(1rem, 1.35vw, 1.45rem) !important;
                box-shadow: 0 16px 54px rgba(2, 6, 23, 0.18) !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput label,
            .block-container:has(.runev-driver-auth-page) .stTextInput label,
            .block-container:has(.runev-auth-page) .stCheckbox label,
            .block-container:has(.runev-driver-auth-page) .stCheckbox label {
                color: #f8fafc !important;
                font-weight: 750 !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input,
            .block-container:has(.runev-driver-auth-page) .stTextInput input {
                min-height: 3rem !important;
                border-radius: 14px !important;
                border: 1px solid rgba(226, 232, 240, 0.85) !important;
                background: rgba(71, 85, 105, 0.82) !important;
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input::placeholder,
            .block-container:has(.runev-driver-auth-page) .stTextInput input::placeholder {
                color: rgba(248, 250, 252, 0.76) !important;
            }

            .block-container:has(.runev-auth-page) .stButton > button,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button,
            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > a,
            .block-container:has(.runev-driver-auth-page) .stButton > button,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button {
                min-height: 3.25rem !important;
                border-radius: 16px !important;
                background: linear-gradient(135deg, #12d6b0, #6478f6, #9b7cf6) !important;
                border: 0 !important;
                color: #ffffff !important;
                font-weight: 760 !important;
                box-shadow: 0 18px 50px rgba(20, 230, 176, 0.18) !important;
            }

            .runev-auth-visual,
            .runev-driver-auth-visual {
                height: 100% !important;
                min-height: 0 !important;
                padding: clamp(1.25rem, 2vw, 1.75rem) !important;
                border-radius: 24px !important;
                border: 1px solid rgba(148, 163, 184, 0.20) !important;
                background: rgba(17, 24, 39, 0.72) !important;
                box-shadow: 0 24px 70px rgba(2, 6, 23, 0.34) !important;
            }

            .runev-auth-visual h2,
            .runev-driver-auth-visual h2 {
                margin: clamp(1.6rem, 4vh, 2.35rem) 0 clamp(1.2rem, 3vh, 1.8rem) !important;
                color: #f8fafc !important;
                font-size: clamp(2.05rem, 3.1vw, 3.25rem) !important;
                line-height: 1.14 !important;
                font-weight: 850 !important;
            }

            .runev-auth-visual p,
            .runev-driver-auth-visual p {
                color: #f8fafc !important;
                font-size: clamp(1rem, 1.35vw, 1.2rem) !important;
                line-height: 1.7 !important;
                font-weight: 700 !important;
            }

            .runev-auth-preview-grid,
            .runev-fleet-preview-grid,
            .runev-driver-activity {
                margin-top: clamp(1.15rem, 4vh, 2.5rem) !important;
            }

            .runev-auth-legal {
                color: #94a3b8 !important;
                font-size: 0.82rem !important;
                margin-top: 0.75rem !important;
            }

            @media (max-height: 820px) and (min-width: 901px) {
                .block-container:has(.runev-auth-page),
                .block-container:has(.runev-driver-auth-page) {
                    padding-top: 1.35rem !important;
                }

                .runev-auth-heading,
                .runev-driver-auth-heading {
                    min-height: 150px !important;
                    padding: 1.35rem 1.75rem !important;
                    margin-bottom: 1rem !important;
                }

                .runev-auth-heading h1,
                .runev-driver-auth-heading h1 {
                    font-size: 2.55rem !important;
                }

                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"],
                .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                    height: calc(100svh - 188px) !important;
                }

                .runev-auth-card-copy h2,
                .runev-driver-auth-copy h2 {
                    margin-bottom: 3.2rem !important;
                }

                .runev-auth-visual h2,
                .runev-driver-auth-visual h2 {
                    font-size: 2.55rem !important;
                    margin-top: 1.4rem !important;
                }
            }

            @media (max-width: 900px) {
                .block-container:has(.runev-auth-page),
                .block-container:has(.runev-driver-auth-page) {
                    height: auto !important;
                    min-height: 100svh !important;
                    overflow-y: auto !important;
                }

                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"],
                .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                    height: auto !important;
                }

                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"],
                .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"] {
                    width: 100% !important;
                }

                .runev-auth-card-copy h2,
                .runev-driver-auth-copy h2 {
                    margin: 0.7rem 0 1.2rem !important;
                }
            }

            /* Final deployed-login match: mirrors the shared production screenshots. */
            .stApp:has(.runev-auth-page),
            .stApp:has(.runev-driver-auth-page) {
                background:
                    linear-gradient(135deg, rgba(8, 20, 31, 0.98), rgba(12, 20, 36, 0.98) 50%, rgba(16, 25, 43, 0.98)),
                    #0b1220 !important;
            }

            .block-container:has(.runev-auth-page),
            .block-container:has(.runev-driver-auth-page) {
                width: 100% !important;
                max-width: none !important;
                height: auto !important;
                min-height: 100svh !important;
                padding: 3.2rem 2.25rem 0.5rem !important;
                overflow: auto !important;
                display: block !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stVerticalBlock"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stVerticalBlock"] {
                gap: 0 !important;
            }

            .runev-auth-heading,
            .runev-driver-auth-heading {
                width: 100% !important;
                min-height: 204px !important;
                height: 204px !important;
                margin: 0 0 1.55rem !important;
                padding: 2rem 2.1rem !important;
                border-radius: 30px !important;
                border: 1px solid rgba(148, 163, 184, 0.22) !important;
                background:
                    linear-gradient(90deg, rgba(13, 82, 78, 0.62), rgba(27, 49, 78, 0.78) 48%, rgba(31, 41, 55, 0.78)),
                    #172033 !important;
                box-shadow: none !important;
                box-sizing: border-box !important;
            }

            .runev-auth-heading span,
            .runev-driver-auth-heading span {
                display: block !important;
                margin: 0 0 0.75rem !important;
                color: #14e6b0 !important;
                font-size: 1rem !important;
                line-height: 1.1 !important;
                font-weight: 850 !important;
                letter-spacing: 0.11em !important;
                text-transform: uppercase !important;
            }

            .runev-auth-heading h1,
            .runev-driver-auth-heading h1,
            .runev-auth-main-title {
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                margin: 0 !important;
                max-width: 1280px !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: clamp(3rem, 3vw, 3.7rem) !important;
                line-height: 1.08 !important;
                font-weight: 850 !important;
                letter-spacing: 0 !important;
                text-transform: none !important;
            }

            .runev-auth-heading p,
            .runev-driver-auth-heading p {
                margin: 1rem 0 0 !important;
                max-width: 1280px !important;
                color: #cbd5e1 !important;
                -webkit-text-fill-color: #cbd5e1 !important;
                font-size: 1.25rem !important;
                line-height: 1.45 !important;
                font-weight: 700 !important;
                text-transform: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                width: 100% !important;
                max-width: none !important;
                height: auto !important;
                min-height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                gap: 1.5rem !important;
                align-items: stretch !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child,
            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child,
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child,
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child {
                display: flex !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2),
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) {
                flex: 0 0 calc(45% - 0.75rem) !important;
                width: calc(45% - 0.75rem) !important;
                max-width: calc(45% - 0.75rem) !important;
                min-width: 0 !important;
                padding: 0 !important;
                background: transparent !important;
                border: 0 !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3),
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) {
                flex: 0 0 calc(55% - 0.75rem) !important;
                width: calc(55% - 0.75rem) !important;
                max-width: calc(55% - 0.75rem) !important;
                min-width: 0 !important;
                padding: 0 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="column"]:has(.runev-auth-card-copy),
            .block-container:has(.runev-driver-auth-page) [data-testid="column"]:has(.runev-driver-auth-copy) {
                overflow: visible !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child,
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child {
                flex: 0 0 calc(45% - 0.75rem) !important;
                width: calc(45% - 0.75rem) !important;
                max-width: calc(45% - 0.75rem) !important;
                min-width: 0 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child,
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child {
                flex: 0 0 calc(55% - 0.75rem) !important;
                width: calc(55% - 0.75rem) !important;
                max-width: calc(55% - 0.75rem) !important;
                min-width: 0 !important;
            }

            .runev-auth-card-copy,
            .runev-driver-auth-copy,
            .block-container:has(.runev-auth-page) .runev-auth-divider {
                display: none !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"],
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] {
                display: flex !important;
                align-items: flex-end !important;
                justify-content: flex-start !important;
                flex-wrap: nowrap !important;
                gap: 1.45rem !important;
                height: 3.85rem !important;
                margin: 0 !important;
                padding: 0 !important;
                border-bottom: 1px solid rgba(148, 163, 184, 0.13) !important;
                overflow: hidden !important;
                background: transparent !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button,
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: auto !important;
                min-width: max-content !important;
                max-width: none !important;
                height: 3.85rem !important;
                min-height: 3.85rem !important;
                margin: 0 !important;
                padding: 0 0.08rem !important;
                border: 0 !important;
                border-radius: 0 !important;
                background: transparent !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                box-shadow: none !important;
                font-size: 1.05rem !important;
                font-weight: 760 !important;
                line-height: 1 !important;
                white-space: nowrap !important;
                text-transform: none !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button:nth-child(3),
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label:nth-child(3),
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label > div:first-child {
                display: none !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button[aria-selected="true"],
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label:has(input:checked) {
                border-bottom: 3px solid #ff3b5f !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [data-baseweb="tab-panel"],
            .block-container:has(.runev-auth-page) form,
            .block-container:has(.runev-driver-auth-page) form {
                margin-top: 1.35rem !important;
                padding: 1.55rem 1.45rem !important;
                border-radius: 10px !important;
                border: 1px solid rgba(148, 163, 184, 0.10) !important;
                background: rgba(15, 23, 42, 0.18) !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput label,
            .block-container:has(.runev-driver-auth-page) .stTextInput label,
            .block-container:has(.runev-auth-page) .stCheckbox label,
            .block-container:has(.runev-driver-auth-page) .stCheckbox label {
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 1rem !important;
                font-weight: 760 !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input,
            .block-container:has(.runev-driver-auth-page) .stTextInput input {
                min-height: 3.05rem !important;
                border-radius: 14px !important;
                border: 1.5px solid rgba(226, 232, 240, 0.92) !important;
                background: rgba(71, 85, 105, 0.88) !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) .stButton > button,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button,
            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > a,
            .block-container:has(.runev-driver-auth-page) .stButton > button,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button {
                min-height: 3.25rem !important;
                border-radius: 16px !important;
                background: linear-gradient(135deg, #12d6b0 0%, #5d7cf4 67%, #9b7cf6 100%) !important;
                border: 0 !important;
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                font-size: 1.08rem !important;
                font-weight: 760 !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-driver-auth-page) form + [data-testid="stHorizontalBlock"] {
                display: none !important;
            }

            .runev-auth-visual,
            .runev-driver-auth-visual {
                height: 100% !important;
                min-height: 0 !important;
                padding: 1.55rem 1.7rem !important;
                border-radius: 24px !important;
                border: 1px solid rgba(148, 163, 184, 0.20) !important;
                background: rgba(17, 24, 39, 0.72) !important;
                box-shadow: none !important;
                overflow: hidden !important;
            }

            .runev-auth-visual h2,
            .runev-driver-auth-visual h2 {
                margin: 1.85rem 0 1.2rem !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: clamp(2.7rem, 3vw, 3.25rem) !important;
                line-height: 1.18 !important;
                font-weight: 850 !important;
                letter-spacing: 0 !important;
                text-transform: none !important;
            }

            .runev-auth-visual p,
            .runev-driver-auth-visual p {
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 1.15rem !important;
                line-height: 1.75 !important;
                font-weight: 720 !important;
                max-width: 100% !important;
            }

            .runev-auth-preview-grid,
            .runev-fleet-preview-grid,
            .runev-driver-activity {
                display: none !important;
            }

            @media (max-height: 820px) and (min-width: 901px) {
                .block-container:has(.runev-auth-page),
                .block-container:has(.runev-driver-auth-page) {
                    padding-top: 2.25rem !important;
                }

                .runev-auth-heading,
                .runev-driver-auth-heading {
                    height: 205px !important;
                    min-height: 205px !important;
                    margin-bottom: 1.55rem !important;
                }

                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"],
                .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                    height: auto !important;
                }

                .runev-auth-heading h1,
                .runev-driver-auth-heading h1 {
                    font-size: 2.9rem !important;
                }

                .runev-auth-visual h2,
                .runev-driver-auth-visual h2 {
                    font-size: 2.65rem !important;
                }
            }

            /* Hard auth geometry correction for the deployed screenshot proportions. */
            .block-container:has(.runev-auth-page),
            .block-container:has(.runev-driver-auth-page) {
                padding: 3.05rem 2rem 0 !important;
                overflow: auto !important;
            }

            .runev-auth-heading,
            .runev-driver-auth-heading {
                height: 205px !important;
                min-height: 205px !important;
                max-height: 205px !important;
                margin-bottom: 1.45rem !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                height: auto !important;
                max-height: none !important;
                gap: 1.55rem !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child,
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child {
                flex: 0 0 calc(45% - 0.8rem) !important;
                width: calc(45% - 0.8rem) !important;
                max-width: calc(45% - 0.8rem) !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child,
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child {
                flex: 0 0 calc(55% - 0.8rem) !important;
                width: calc(55% - 0.8rem) !important;
                max-width: calc(55% - 0.8rem) !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"],
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] {
                height: 3.35rem !important;
                min-height: 3.35rem !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] {
                height: 2.9rem !important;
                min-height: 2.9rem !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button,
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label {
                height: 3.35rem !important;
                min-height: 3.35rem !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button {
                height: 2.9rem !important;
                min-height: 2.9rem !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [data-baseweb="tab-panel"],
            .block-container:has(.runev-auth-page) form,
            .block-container:has(.runev-driver-auth-page) form {
                margin-top: 0.75rem !important;
                padding: 1.2rem 1.35rem !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input,
            .block-container:has(.runev-driver-auth-page) .stTextInput input {
                min-height: 2.7rem !important;
            }

            .block-container:has(.runev-auth-page) .stButton > button,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button,
            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > a,
            .block-container:has(.runev-driver-auth-page) .stButton > button,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button {
                min-height: 3rem !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] {
                display: block !important;
                margin: 0 0 0.9rem !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > a {
                justify-content: center !important;
                text-decoration: none !important;
            }

            .runev-auth-visual,
            .runev-driver-auth-visual {
                padding: 1.5rem 1.75rem !important;
            }

            .runev-auth-visual h2,
            .runev-driver-auth-visual h2 {
                font-size: clamp(2.55rem, 2.65vw, 3.05rem) !important;
                line-height: 1.18 !important;
                margin: 1.55rem 0 1rem !important;
            }

            .runev-auth-visual p,
            .runev-driver-auth-visual p {
                font-size: 1.08rem !important;
                line-height: 1.6 !important;
            }

            /* Size correction: keep the deployed look, but reduce oversized local elements. */
            .block-container:has(.runev-auth-page),
            .block-container:has(.runev-driver-auth-page) {
                padding-top: 2.1rem !important;
            }

            .runev-auth-heading,
            .runev-driver-auth-heading {
                height: 170px !important;
                min-height: 170px !important;
                max-height: 170px !important;
                margin-bottom: 1.1rem !important;
            }

            .runev-auth-main-title {
                font-size: clamp(2.45rem, 2.75vw, 3.2rem) !important;
                line-height: 1.06 !important;
            }

            .runev-auth-heading p,
            .runev-driver-auth-heading p {
                font-size: 1.12rem !important;
                margin-top: 0.65rem !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                height: auto !important;
                max-height: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] {
                margin-bottom: 0.55rem !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"],
            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button,
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"],
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label {
                height: 2.55rem !important;
                min-height: 2.55rem !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [data-baseweb="tab-panel"],
            .block-container:has(.runev-auth-page) form,
            .block-container:has(.runev-driver-auth-page) form {
                margin-top: 0.6rem !important;
                padding: 0.95rem 1.15rem !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input,
            .block-container:has(.runev-driver-auth-page) .stTextInput input {
                min-height: 2.45rem !important;
            }

            .block-container:has(.runev-auth-page) .stButton > button,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button,
            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > a,
            .block-container:has(.runev-driver-auth-page) .stButton > button,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button {
                min-height: 2.75rem !important;
            }

            .runev-auth-visual,
            .runev-driver-auth-visual {
                padding: 1.25rem 1.45rem !important;
            }

            .runev-auth-visual h2,
            .runev-driver-auth-visual h2 {
                font-size: clamp(2.1rem, 2.45vw, 2.85rem) !important;
                line-height: 1.16 !important;
                margin: 1.15rem 0 0.75rem !important;
            }

            .runev-auth-visual p,
            .runev-driver-auth-visual p {
                font-size: 1rem !important;
                line-height: 1.52 !important;
            }

            /* Product authentication experience: no landing heroes, no marketing layout. */
            .stApp:has(.runev-auth-page),
            .stApp:has(.runev-driver-auth-page) {
                background:
                    radial-gradient(circle at 12% 0%, rgba(20, 230, 176, 0.10), transparent 24rem),
                    linear-gradient(135deg, #08111f 0%, #0d1728 52%, #111827 100%) !important;
            }

            .block-container:has(.runev-auth-page),
            .block-container:has(.runev-driver-auth-page) {
                width: 100% !important;
                max-width: none !important;
                height: auto !important;
                min-height: 100vh !important;
                padding: 0 !important;
                overflow: auto !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                box-sizing: border-box !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-heading,
            .block-container:has(.runev-auth-page) .runev-auth-visual,
            .block-container:has(.runev-driver-auth-page) .runev-driver-auth-heading,
            .block-container:has(.runev-driver-auth-page) .runev-driver-auth-visual {
                display: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) {
                width: min(460px, calc(100vw - 2rem)) !important;
                max-width: 460px !important;
                height: auto !important;
                max-height: none !important;
                margin: 0 auto !important;
                display: flex !important;
                gap: 0 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:not(:has(.runev-user-auth-card)) {
                display: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:has(.runev-user-auth-card) {
                flex: 0 0 100% !important;
                width: 100% !important;
                max-width: 100% !important;
                min-width: 0 !important;
                padding: 0 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="column"]:has(.runev-user-auth-card) {
                padding: 1.35rem !important;
                border: 1px solid rgba(148, 163, 184, 0.18) !important;
                border-radius: 20px !important;
                background: rgba(15, 23, 42, 0.78) !important;
                box-shadow: 0 24px 70px rgba(2, 6, 23, 0.30) !important;
                backdrop-filter: blur(18px);
            }

            .runev-user-auth-card,
            .runev-driver-auth-title {
                margin: 0 0 0.85rem !important;
                padding: 0 !important;
                text-align: left !important;
            }

            .runev-auth-logo {
                width: max-content;
                margin-bottom: 0.75rem;
                color: #14e6b0 !important;
                font-size: 0.82rem;
                font-weight: 850;
                letter-spacing: 0.13em;
                text-transform: uppercase;
            }

            .runev-user-auth-card h1,
            .runev-driver-auth-title h1 {
                margin: 0 !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 1.45rem !important;
                line-height: 1.16 !important;
                font-weight: 820 !important;
                letter-spacing: 0 !important;
            }

            .runev-user-auth-card p {
                margin: 0.45rem 0 0 !important;
                color: #94a3b8 !important;
                -webkit-text-fill-color: #94a3b8 !important;
                font-size: 0.92rem !important;
                line-height: 1.45 !important;
                font-weight: 580 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] {
                display: block !important;
                margin: 0 0 0.75rem !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-divider {
                display: flex !important;
                margin: 0.7rem 0 !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"],
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] {
                height: 2.35rem !important;
                min-height: 2.35rem !important;
                gap: 1rem !important;
                border-bottom: 1px solid rgba(148, 163, 184, 0.14) !important;
                margin: 0 0 0.75rem !important;
                padding: 0 !important;
                overflow: hidden !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button,
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label {
                height: 2.35rem !important;
                min-height: 2.35rem !important;
                padding: 0 !important;
                border: 0 !important;
                border-radius: 0 !important;
                background: transparent !important;
                color: #e2e8f0 !important;
                -webkit-text-fill-color: #e2e8f0 !important;
                font-size: 0.92rem !important;
                font-weight: 720 !important;
                box-shadow: none !important;
                white-space: nowrap !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button:nth-child(3) {
                display: inline-flex !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [data-baseweb="tab-panel"],
            .block-container:has(.runev-auth-page) form,
            .block-container:has(.runev-driver-auth-page) form {
                margin: 0 !important;
                padding: 0 !important;
                border: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput,
            .block-container:has(.runev-driver-auth-page) .stTextInput {
                margin-bottom: 0.45rem !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput label,
            .block-container:has(.runev-driver-auth-page) .stTextInput label,
            .block-container:has(.runev-auth-page) .stCheckbox label,
            .block-container:has(.runev-driver-auth-page) .stCheckbox label {
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 0.88rem !important;
                font-weight: 680 !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input,
            .block-container:has(.runev-driver-auth-page) .stTextInput input {
                min-height: 2.55rem !important;
                height: 2.55rem !important;
                border-radius: 10px !important;
                border: 1px solid rgba(148, 163, 184, 0.24) !important;
                background: rgba(15, 23, 42, 0.72) !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                box-shadow: none !important;
                font-size: 0.95rem !important;
            }

            .block-container:has(.runev-auth-page) .stButton > button,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button,
            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > a,
            .block-container:has(.runev-driver-auth-page) .stButton > button,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button {
                min-height: 2.6rem !important;
                height: 2.6rem !important;
                border-radius: 10px !important;
                background: linear-gradient(135deg, #10d9b0, #6178f6) !important;
                border: 0 !important;
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                font-size: 0.95rem !important;
                font-weight: 720 !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) .stCheckbox,
            .block-container:has(.runev-driver-auth-page) .stCheckbox {
                margin: 0.1rem 0 0.55rem !important;
            }

            .runev-auth-legal {
                margin-top: 0.75rem !important;
                color: #94a3b8 !important;
                font-size: 0.78rem !important;
                line-height: 1.4 !important;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-driver-auth-title):has(.runev-driver-preview) {
                width: min(1180px, calc(100vw - 3rem)) !important;
                height: min(640px, calc(100vh - 3rem)) !important;
                max-height: calc(100vh - 3rem) !important;
                margin: 0 auto !important;
                gap: 1.5rem !important;
                align-items: stretch !important;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-driver-auth-title):has(.runev-driver-preview) > [data-testid="column"]:first-child {
                flex: 0 0 calc(40% - 0.75rem) !important;
                width: calc(40% - 0.75rem) !important;
                max-width: calc(40% - 0.75rem) !important;
                min-width: 0 !important;
                padding: 1.35rem !important;
                border: 1px solid rgba(148, 163, 184, 0.18) !important;
                border-radius: 20px !important;
                background: rgba(15, 23, 42, 0.78) !important;
                box-shadow: 0 24px 70px rgba(2, 6, 23, 0.26) !important;
            }

            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-driver-auth-title):has(.runev-driver-preview) > [data-testid="column"]:last-child {
                flex: 0 0 calc(60% - 0.75rem) !important;
                width: calc(60% - 0.75rem) !important;
                max-width: calc(60% - 0.75rem) !important;
                min-width: 0 !important;
                padding: 0 !important;
            }

            .runev-driver-auth-copy {
                display: none !important;
            }

            .runev-driver-preview {
                height: 100%;
                padding: 1.5rem;
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 24px;
                background:
                    linear-gradient(135deg, rgba(20, 230, 176, 0.10), transparent 35%),
                    rgba(17, 24, 39, 0.76);
                box-shadow: 0 24px 70px rgba(2, 6, 23, 0.26);
                box-sizing: border-box;
            }

            .runev-preview-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.2rem;
                color: #94a3b8;
                font-size: 0.86rem;
                font-weight: 720;
            }

            .runev-preview-top strong {
                color: #14e6b0;
            }

            .runev-preview-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.85rem;
            }

            .runev-preview-grid div,
            .runev-preview-table {
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: 16px;
                background: rgba(15, 23, 42, 0.62);
            }

            .runev-preview-grid div {
                padding: 1rem;
            }

            .runev-preview-grid span,
            .runev-preview-table span {
                display: block;
                color: #94a3b8;
                font-size: 0.78rem;
                font-weight: 760;
            }

            .runev-preview-grid strong {
                display: block;
                margin-top: 0.45rem;
                color: #f8fafc;
                font-size: 1.7rem;
                line-height: 1;
                font-weight: 850;
            }

            .runev-preview-table {
                margin-top: 1rem;
                padding: 0.45rem 0;
            }

            .runev-preview-table div {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                padding: 0.75rem 1rem;
                border-bottom: 1px solid rgba(148, 163, 184, 0.10);
            }

            .runev-preview-table div:last-child {
                border-bottom: 0;
            }

            .runev-preview-table b {
                color: #e2e8f0;
                font-size: 0.84rem;
            }

            @media (max-width: 900px) {
                .block-container:has(.runev-auth-page),
                .block-container:has(.runev-driver-auth-page) {
                    height: auto !important;
                    min-height: 100vh !important;
                    overflow-y: auto !important;
                    padding: 1rem !important;
                }

                .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-driver-auth-title):has(.runev-driver-preview) {
                    width: 100% !important;
                    height: auto !important;
                    display: block !important;
                }

                .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-driver-auth-title):has(.runev-driver-preview) > [data-testid="column"] {
                    width: 100% !important;
                    max-width: 100% !important;
                }
            }

            /* RunEV v2.0 final rule: preserve deployed horizontal product structure. */
            .block-container:has(.runev-auth-page),
            .block-container:has(.runev-driver-auth-page) {
                width: 100% !important;
                max-width: 100% !important;
                min-height: 100vh !important;
                height: 100vh !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: stretch !important;
                justify-content: flex-start !important;
                padding: 2rem 2.35rem 0.7rem !important;
                overflow: hidden !important;
                box-sizing: border-box !important;
                background:
                    radial-gradient(circle at 10% 4%, rgba(20, 230, 176, 0.10), transparent 24rem),
                    linear-gradient(135deg, #08111f 0%, #0d1728 54%, #111827 100%) !important;
            }

            .block-container:has(.runev-auth-page) > div,
            .block-container:has(.runev-driver-auth-page) > div {
                width: 100% !important;
            }

            .runev-auth-heading,
            .runev-driver-auth-heading {
                display: block !important;
                width: 100% !important;
                height: auto !important;
                min-height: 155px !important;
                max-height: none !important;
                margin: 0 0 1.45rem !important;
                padding: 1.9rem 2.1rem !important;
                border-radius: 30px !important;
                border: 1px solid rgba(148, 163, 184, 0.22) !important;
                background:
                    linear-gradient(90deg, rgba(13, 82, 78, 0.62), rgba(27, 49, 78, 0.78) 48%, rgba(31, 41, 55, 0.78)),
                    #172033 !important;
                box-shadow: 0 24px 70px rgba(2, 6, 23, 0.18) !important;
                box-sizing: border-box !important;
            }

            .runev-auth-heading span,
            .runev-driver-auth-heading span {
                display: block !important;
                margin: 0 0 0.75rem !important;
                color: #14e6b0 !important;
                -webkit-text-fill-color: #14e6b0 !important;
                font-size: 0.9rem !important;
                line-height: 1.1 !important;
                font-weight: 850 !important;
                letter-spacing: 0.12em !important;
                text-transform: uppercase !important;
            }

            .runev-auth-main-title,
            .runev-auth-heading h1,
            .runev-driver-auth-heading h1 {
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                margin: 0 !important;
                max-width: 1240px !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: clamp(2.65rem, 3.1vw, 3.45rem) !important;
                line-height: 1.05 !important;
                font-weight: 850 !important;
                letter-spacing: 0 !important;
                text-transform: none !important;
            }

            .runev-auth-heading p,
            .runev-driver-auth-heading p {
                display: block !important;
                margin: 0.75rem 0 0 !important;
                max-width: 1240px !important;
                color: #cbd5e1 !important;
                -webkit-text-fill-color: #cbd5e1 !important;
                font-size: 1.05rem !important;
                line-height: 1.45 !important;
                font-weight: 680 !important;
                text-transform: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                width: 100% !important;
                max-width: none !important;
                height: auto !important;
                max-height: none !important;
                min-height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                gap: 1.4rem !important;
                align-items: stretch !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"] {
                display: flex !important;
                flex: unset !important;
                width: auto !important;
                max-width: none !important;
                min-width: 0 !important;
                padding: 0 !important;
                background: transparent !important;
                border: 0 !important;
                box-shadow: none !important;
            }

            .runev-auth-card-copy,
            .runev-driver-auth-copy,
            .runev-auth-visual,
            .runev-driver-auth-visual {
                display: block !important;
            }

            .runev-auth-card-copy,
            .runev-driver-auth-copy {
                margin: 0 0 0.85rem !important;
                color: #f8fafc !important;
            }

            .runev-auth-card-copy h2,
            .runev-driver-auth-copy h2 {
                margin: 0.35rem 0 0.45rem !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 1.2rem !important;
                line-height: 1.15 !important;
                font-weight: 820 !important;
                letter-spacing: 0 !important;
                text-transform: none !important;
            }

            .runev-auth-card-copy p,
            .runev-driver-auth-copy p {
                margin: 0 !important;
                color: #cbd5e1 !important;
                -webkit-text-fill-color: #cbd5e1 !important;
                font-size: 0.94rem !important;
                line-height: 1.45 !important;
                font-weight: 620 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"],
            .block-container:has(.runev-auth-page) .runev-auth-divider {
                display: flex !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] {
                margin-bottom: 0.65rem !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-divider {
                margin: 0.6rem 0 !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"],
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] {
                height: 2.6rem !important;
                min-height: 2.6rem !important;
                gap: 1.1rem !important;
                border-bottom: 1px solid rgba(148, 163, 184, 0.14) !important;
                margin: 0 0 0.85rem !important;
                padding: 0 !important;
                background: transparent !important;
                overflow: hidden !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button,
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: auto !important;
                min-width: max-content !important;
                height: 2.6rem !important;
                min-height: 2.6rem !important;
                margin: 0 !important;
                padding: 0 0.05rem !important;
                border: 0 !important;
                border-radius: 0 !important;
                background: transparent !important;
                color: #e2e8f0 !important;
                -webkit-text-fill-color: #e2e8f0 !important;
                font-size: 0.92rem !important;
                font-weight: 720 !important;
                box-shadow: none !important;
                white-space: nowrap !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button[aria-selected="true"],
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label:has(input:checked) {
                border-bottom: 3px solid #ff3b5f !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [data-baseweb="tab-panel"],
            .block-container:has(.runev-auth-page) form,
            .block-container:has(.runev-driver-auth-page) form {
                margin: 0 !important;
                padding: 1rem 1.15rem !important;
                border: 1px solid rgba(148, 163, 184, 0.11) !important;
                border-radius: 12px !important;
                background: rgba(15, 23, 42, 0.20) !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input,
            .block-container:has(.runev-driver-auth-page) .stTextInput input {
                min-height: 2.7rem !important;
                height: 2.7rem !important;
                border-radius: 12px !important;
                border: 1.5px solid rgba(226, 232, 240, 0.86) !important;
                background: rgba(71, 85, 105, 0.82) !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                box-shadow: none !important;
                font-size: 0.95rem !important;
            }

            .block-container:has(.runev-auth-page) .stButton > button,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button,
            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > a,
            .block-container:has(.runev-driver-auth-page) .stButton > button,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button {
                min-height: 2.85rem !important;
                height: 2.85rem !important;
                border-radius: 14px !important;
                background: linear-gradient(135deg, #10d9b0, #6178f6, #9b7cf6) !important;
                border: 0 !important;
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                font-size: 0.98rem !important;
                font-weight: 740 !important;
                box-shadow: 0 16px 40px rgba(20, 230, 176, 0.14) !important;
            }

            .runev-auth-visual,
            .runev-driver-auth-visual {
                height: 100% !important;
                min-height: 0 !important;
                padding: 1.6rem 1.7rem !important;
                border-radius: 24px !important;
                border: 1px solid rgba(148, 163, 184, 0.20) !important;
                background: rgba(17, 24, 39, 0.72) !important;
                box-shadow: 0 24px 70px rgba(2, 6, 23, 0.22) !important;
                overflow: hidden !important;
            }

            .runev-auth-visual h2,
            .runev-driver-auth-visual h2 {
                margin: 1.4rem 0 0.95rem !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: clamp(2.25rem, 2.65vw, 3rem) !important;
                line-height: 1.15 !important;
                font-weight: 850 !important;
                letter-spacing: 0 !important;
                text-transform: none !important;
            }

            .runev-auth-visual p,
            .runev-driver-auth-visual p {
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 1rem !important;
                line-height: 1.55 !important;
                font-weight: 700 !important;
                max-width: 100% !important;
            }

            @media (max-height: 820px) and (min-width: 901px) {
                .block-container:has(.runev-auth-page),
                .block-container:has(.runev-driver-auth-page) {
                    padding-top: 1.55rem !important;
                }

                .runev-auth-heading,
                .runev-driver-auth-heading {
                    min-height: 145px !important;
                    margin-bottom: 1rem !important;
                    padding: 1.45rem 1.8rem !important;
                }

                .runev-auth-main-title,
                .runev-auth-heading h1,
                .runev-driver-auth-heading h1 {
                    font-size: 2.65rem !important;
                }

                .runev-auth-heading p,
                .runev-driver-auth-heading p {
                    font-size: 1rem !important;
                }

                .runev-auth-card-copy,
                .runev-driver-auth-copy {
                    display: none !important;
                }
            }

            /*
             * Exact deployed auth layout override.
             * UI only: keeps Streamlit/Python workflows intact and restores the
             * original RunEV horizontal landing/auth composition from production.
             */
            .block-container:has(.runev-auth-page),
            .block-container:has(.runev-driver-auth-page) {
                width: 100vw !important;
                max-width: 100vw !important;
                min-height: 100vh !important;
                height: 100vh !important;
                margin: 0 !important;
                padding: 2.9rem 2.35rem 0.65rem !important;
                overflow: hidden !important;
                box-sizing: border-box !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: flex-start !important;
                align-items: stretch !important;
                background:
                    radial-gradient(circle at 18% 28%, rgba(20, 230, 176, 0.13), transparent 29rem),
                    linear-gradient(135deg, #07131f 0%, #111a2c 58%, #13213a 100%) !important;
                color: #f8fafc !important;
            }

            .block-container:has(.runev-auth-page) > div,
            .block-container:has(.runev-driver-auth-page) > div {
                width: 100% !important;
                max-width: none !important;
            }

            .runev-auth-heading,
            .runev-driver-auth-heading {
                width: 100% !important;
                max-width: none !important;
                height: 205px !important;
                min-height: 205px !important;
                margin: 0 0 1.55rem !important;
                padding: 2.2rem 2.15rem !important;
                border-radius: 30px !important;
                border: 1px solid rgba(148, 163, 184, 0.20) !important;
                background:
                    linear-gradient(90deg, rgba(14, 88, 82, 0.72) 0%, rgba(29, 47, 74, 0.76) 49%, rgba(31, 39, 53, 0.86) 100%) !important;
                box-shadow: none !important;
                color: #f8fafc !important;
                overflow: hidden !important;
            }

            .runev-auth-heading span,
            .runev-driver-auth-heading span {
                display: block !important;
                margin: 0 0 0.65rem !important;
                color: #14e6b0 !important;
                -webkit-text-fill-color: #14e6b0 !important;
                font-size: 0.92rem !important;
                line-height: 1.1 !important;
                font-weight: 850 !important;
                letter-spacing: 0.13em !important;
                text-transform: uppercase !important;
            }

            .runev-auth-main-title,
            .runev-auth-heading h1,
            .runev-driver-auth-heading h1 {
                display: block !important;
                margin: 0 !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: clamp(2.85rem, 3.15vw, 3.55rem) !important;
                line-height: 1.08 !important;
                font-weight: 850 !important;
                letter-spacing: 0 !important;
                text-transform: none !important;
                white-space: normal !important;
            }

            .runev-auth-heading p,
            .runev-driver-auth-heading p {
                margin: 1rem 0 0 !important;
                max-width: 100% !important;
                color: #cbd5e1 !important;
                -webkit-text-fill-color: #cbd5e1 !important;
                font-size: 1.05rem !important;
                line-height: 1.35 !important;
                font-weight: 650 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                width: 100% !important;
                max-width: none !important;
                margin: 0 !important;
                padding: 0 !important;
                gap: 1.45rem !important;
                align-items: stretch !important;
                min-height: 0 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"],
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"] {
                min-width: 0 !important;
                padding: 0 !important;
                background: transparent !important;
                border: 0 !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child,
            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child,
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child,
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child {
                flex: 0 0 0 !important;
                width: 0 !important;
                max-width: 0 !important;
                overflow: hidden !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2),
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) {
                flex: 0 0 44.5% !important;
                max-width: 44.5% !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3),
            .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(3) {
                flex: 1 1 auto !important;
                max-width: none !important;
            }

            .runev-auth-card-copy,
            .runev-driver-auth-copy,
            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"],
            .block-container:has(.runev-auth-page) .runev-auth-divider {
                display: none !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"],
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] {
                height: 3rem !important;
                min-height: 3rem !important;
                gap: 1.25rem !important;
                margin: 0 0 1.25rem !important;
                padding: 0 !important;
                border-bottom: 1px solid rgba(148, 163, 184, 0.10) !important;
                background: transparent !important;
                overflow: visible !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button,
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label {
                min-width: 0 !important;
                width: auto !important;
                height: 3rem !important;
                min-height: 3rem !important;
                margin: 0 !important;
                padding: 0 0.05rem !important;
                border: 0 !important;
                border-radius: 0 !important;
                background: transparent !important;
                color: #e5e7eb !important;
                -webkit-text-fill-color: #e5e7eb !important;
                font-size: 1rem !important;
                line-height: 1 !important;
                font-weight: 730 !important;
                box-shadow: none !important;
                white-space: nowrap !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button[aria-selected="true"],
            .block-container:has(.runev-driver-auth-page) div[role="radiogroup"] label:has(input:checked) {
                border-bottom: 3px solid #ff3b5f !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [data-baseweb="tab-panel"],
            .block-container:has(.runev-auth-page) form,
            .block-container:has(.runev-driver-auth-page) form {
                width: 100% !important;
                margin: 0 !important;
                padding: 1.65rem 1.45rem !important;
                border: 1px solid rgba(148, 163, 184, 0.08) !important;
                border-radius: 10px !important;
                background: rgba(15, 23, 42, 0.18) !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput,
            .block-container:has(.runev-driver-auth-page) .stTextInput {
                margin-bottom: 0.95rem !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput label,
            .block-container:has(.runev-driver-auth-page) .stTextInput label,
            .block-container:has(.runev-auth-page) .stCheckbox label,
            .block-container:has(.runev-driver-auth-page) .stCheckbox label {
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 0.95rem !important;
                font-weight: 720 !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input,
            .block-container:has(.runev-driver-auth-page) .stTextInput input {
                height: 3.15rem !important;
                min-height: 3.15rem !important;
                border-radius: 12px !important;
                border: 1.5px solid rgba(241, 245, 249, 0.92) !important;
                background: rgba(71, 85, 105, 0.82) !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 1rem !important;
                font-weight: 650 !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) .stButton > button,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button,
            .block-container:has(.runev-driver-auth-page) .stButton > button,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button {
                width: 100% !important;
                height: 3.25rem !important;
                min-height: 3.25rem !important;
                border-radius: 14px !important;
                border: 0 !important;
                background: linear-gradient(135deg, #12d7b2 0%, #4b86ee 56%, #9475ee 100%) !important;
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                font-size: 1rem !important;
                font-weight: 730 !important;
                box-shadow: 0 18px 42px rgba(20, 230, 176, 0.13) !important;
            }

            .runev-auth-visual,
            .runev-driver-auth-visual {
                display: block !important;
                height: 100% !important;
                min-height: 535px !important;
                margin: 0 !important;
                padding: 1.55rem 1.45rem !important;
                border-radius: 24px !important;
                border: 1px solid rgba(148, 163, 184, 0.18) !important;
                background: rgba(17, 24, 39, 0.76) !important;
                box-shadow: none !important;
                overflow: hidden !important;
            }

            .runev-auth-visual h2,
            .runev-driver-auth-visual h2 {
                margin: 1.55rem 0 1.45rem !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: clamp(2.45rem, 3.05vw, 3.3rem) !important;
                line-height: 1.22 !important;
                font-weight: 840 !important;
                letter-spacing: 0 !important;
                text-transform: none !important;
                max-width: 100% !important;
            }

            .runev-auth-visual p,
            .runev-driver-auth-visual p {
                margin: 0 !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 1.05rem !important;
                line-height: 1.55 !important;
                font-weight: 650 !important;
                max-width: 100% !important;
            }

            .runev-auth-preview-grid,
            .runev-fleet-preview-grid,
            .runev-driver-activity {
                display: none !important;
            }

            .runev-auth-visual::after {
                content: "⚡";
                display: block;
                margin-top: 4.2rem;
                margin-left: 2.1rem;
                font-size: 4.2rem;
                line-height: 1;
                filter: drop-shadow(0 16px 24px rgba(251, 113, 133, 0.22));
            }

            .runev-driver-auth-visual::after {
                content: "🚌";
                display: block;
                margin-top: 3.7rem;
                margin-left: 1.1rem;
                font-size: 3.05rem;
                line-height: 1;
            }

            @media (max-width: 900px) {
                .block-container:has(.runev-auth-page),
                .block-container:has(.runev-driver-auth-page) {
                    height: auto !important;
                    min-height: 100vh !important;
                    overflow-y: auto !important;
                    padding: 1rem !important;
                }

                .runev-auth-heading,
                .runev-driver-auth-heading {
                    height: auto !important;
                    min-height: 0 !important;
                    padding: 1.4rem !important;
                    border-radius: 22px !important;
                }

                .runev-auth-main-title,
                .runev-auth-heading h1,
                .runev-driver-auth-heading h1 {
                    font-size: 2rem !important;
                }

                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"],
                .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] {
                    flex-direction: column !important;
                }

                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"],
                .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"] {
                    width: 100% !important;
                    max-width: 100% !important;
                    flex: 1 1 auto !important;
                }

                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child,
                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child,
                .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child,
                .block-container:has(.runev-driver-auth-page) [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child {
                    display: none !important;
                }

                .runev-auth-visual,
                .runev-driver-auth-visual {
                    min-height: 280px !important;
                }
            }

            /* Latest user auth card: keep every sign-in option visible in the compact UI. */
            .stApp:has(.runev-auth-page) {
                background:
                    radial-gradient(circle at 18% 8%, rgba(20, 230, 176, 0.16), transparent 24rem),
                    radial-gradient(circle at 84% 86%, rgba(99, 102, 241, 0.18), transparent 24rem),
                    linear-gradient(135deg, #07111f 0%, #101827 54%, #142136 100%) !important;
            }

            .block-container:has(.runev-auth-page) {
                width: 100vw !important;
                max-width: 100vw !important;
                min-height: 100vh !important;
                height: auto !important;
                margin: 0 !important;
                padding: 1.25rem !important;
                overflow-y: auto !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                box-sizing: border-box !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-heading,
            .block-container:has(.runev-auth-page) .runev-auth-card-copy,
            .block-container:has(.runev-auth-page) .runev-auth-visual {
                display: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) {
                width: min(472px, 100%) !important;
                max-width: 472px !important;
                margin: 0 auto !important;
                gap: 0 !important;
                align-items: stretch !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"] {
                display: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:has(.runev-user-auth-card) {
                display: block !important;
                flex: 0 0 100% !important;
                width: 100% !important;
                max-width: 100% !important;
                padding: 1.35rem !important;
                border: 1px solid rgba(148, 163, 184, 0.20) !important;
                border-radius: 18px !important;
                background: rgba(15, 23, 42, 0.86) !important;
                box-shadow: 0 28px 78px rgba(2, 6, 23, 0.36) !important;
                backdrop-filter: blur(18px) !important;
            }

            .runev-user-auth-card {
                display: block !important;
                margin: 0 0 1rem !important;
                padding: 0 !important;
            }

            .runev-auth-logo {
                width: max-content !important;
                margin: 0 0 0.8rem !important;
                color: #14e6b0 !important;
                -webkit-text-fill-color: #14e6b0 !important;
                font-size: 0.8rem !important;
                font-weight: 850 !important;
                letter-spacing: 0.13em !important;
                text-transform: uppercase !important;
            }

            .runev-user-auth-card h1 {
                margin: 0 !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 1.6rem !important;
                line-height: 1.16 !important;
                font-weight: 840 !important;
                letter-spacing: 0 !important;
            }

            .runev-user-auth-card p {
                margin: 0.45rem 0 0 !important;
                color: #a8b3c5 !important;
                -webkit-text-fill-color: #a8b3c5 !important;
                font-size: 0.93rem !important;
                line-height: 1.45 !important;
                font-weight: 580 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"],
            .block-container:has(.runev-auth-page) .runev-auth-divider {
                display: block !important;
                margin: 0.75rem 0 !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-divider {
                display: flex !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > a {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 100% !important;
                min-height: 2.85rem !important;
                height: 2.85rem !important;
                border-radius: 12px !important;
                border: 1px solid rgba(226, 232, 240, 0.24) !important;
                background: #f8fafc !important;
                color: #111827 !important;
                -webkit-text-fill-color: #111827 !important;
                font-size: 0.96rem !important;
                font-weight: 780 !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] {
                height: 2.55rem !important;
                min-height: 2.55rem !important;
                gap: 0.9rem !important;
                margin: 0.25rem 0 0.85rem !important;
                border-bottom: 1px solid rgba(148, 163, 184, 0.14) !important;
                overflow: visible !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button {
                height: 2.55rem !important;
                min-height: 2.55rem !important;
                padding: 0 !important;
                color: #e5e7eb !important;
                -webkit-text-fill-color: #e5e7eb !important;
                font-size: 0.88rem !important;
                font-weight: 730 !important;
                white-space: nowrap !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button[aria-selected="true"] {
                border-bottom: 3px solid #14e6b0 !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [data-baseweb="tab-panel"],
            .block-container:has(.runev-auth-page) form {
                width: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
                border: 0 !important;
                border-radius: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput {
                margin-bottom: 0.55rem !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput label,
            .block-container:has(.runev-auth-page) .stCheckbox label {
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 0.86rem !important;
                font-weight: 700 !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input {
                height: 2.75rem !important;
                min-height: 2.75rem !important;
                border-radius: 12px !important;
                border: 1px solid rgba(148, 163, 184, 0.28) !important;
                background: rgba(15, 23, 42, 0.72) !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 0.95rem !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) .stButton > button,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button {
                width: 100% !important;
                height: 2.85rem !important;
                min-height: 2.85rem !important;
                border-radius: 12px !important;
                border: 0 !important;
                background: linear-gradient(135deg, #12d7b2 0%, #4b86ee 58%, #7c6df2 100%) !important;
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                font-size: 0.96rem !important;
                font-weight: 760 !important;
                box-shadow: 0 18px 42px rgba(20, 230, 176, 0.13) !important;
            }

            .block-container:has(.runev-auth-page) .stCheckbox {
                margin: 0.1rem 0 0.65rem !important;
            }

            .runev-auth-legal {
                margin-top: 0.9rem !important;
                color: #94a3b8 !important;
                font-size: 0.78rem !important;
                line-height: 1.4 !important;
            }

            @media (max-width: 520px) {
                .block-container:has(.runev-auth-page) {
                    padding: 0.8rem !important;
                    align-items: flex-start !important;
                }

                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:has(.runev-user-auth-card) {
                    padding: 1rem !important;
                    border-radius: 16px !important;
                }

                .runev-user-auth-card h1 {
                    font-size: 1.4rem !important;
                }

                .block-container:has(.runev-auth-page) .stTabs [role="tablist"] {
                    gap: 0.55rem !important;
                }

                .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button {
                    font-size: 0.78rem !important;
                }
            }

            /* Real-app auth layout: wide, horizontal, and non-collapsing. */
            .stApp:has(.runev-auth-page) {
                background:
                    radial-gradient(circle at 12% 20%, rgba(20, 230, 176, 0.16), transparent 28rem),
                    radial-gradient(circle at 92% 78%, rgba(79, 134, 238, 0.16), transparent 30rem),
                    linear-gradient(135deg, #06131f 0%, #0e1728 52%, #142036 100%) !important;
            }

            .block-container:has(.runev-auth-page) {
                width: 100vw !important;
                max-width: 100vw !important;
                min-height: 100vh !important;
                height: auto !important;
                margin: 0 !important;
                padding: clamp(1.4rem, 2.3vw, 2.4rem) !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: stretch !important;
                justify-content: flex-start !important;
                box-sizing: border-box !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-heading {
                display: block !important;
                width: min(100%, 1835px) !important;
                max-width: 1835px !important;
                min-height: 184px !important;
                height: auto !important;
                margin: 0 auto clamp(1.5rem, 2.4vw, 2rem) !important;
                padding: clamp(1.45rem, 2.4vw, 2.2rem) !important;
                border-radius: 30px !important;
                border: 1px solid rgba(148, 163, 184, 0.20) !important;
                background:
                    linear-gradient(90deg, rgba(14, 88, 82, 0.72) 0%, rgba(29, 47, 74, 0.76) 49%, rgba(31, 39, 53, 0.86) 100%) !important;
                box-shadow: none !important;
                overflow: hidden !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-heading span {
                display: block !important;
                margin: 0 0 0.7rem !important;
                color: #14e6b0 !important;
                -webkit-text-fill-color: #14e6b0 !important;
                font-size: 0.92rem !important;
                line-height: 1.1 !important;
                font-weight: 850 !important;
                letter-spacing: 0.13em !important;
                text-transform: uppercase !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-main-title {
                display: block !important;
                max-width: 980px !important;
                margin: 0 !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: clamp(2.45rem, 3.2vw, 3.55rem) !important;
                line-height: 1.08 !important;
                font-weight: 850 !important;
                letter-spacing: 0 !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-heading p {
                max-width: 980px !important;
                margin: 1rem 0 0 !important;
                color: #cbd5e1 !important;
                -webkit-text-fill-color: #cbd5e1 !important;
                font-size: 1.05rem !important;
                line-height: 1.45 !important;
                font-weight: 650 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) {
                width: min(100%, 1835px) !important;
                max-width: 1835px !important;
                min-height: min(540px, calc(100vh - 260px)) !important;
                margin: 0 auto !important;
                gap: clamp(1.4rem, 2.2vw, 2rem) !important;
                align-items: stretch !important;
                display: flex !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"] {
                min-width: 0 !important;
                padding: 0 !important;
                display: block !important;
                background: transparent !important;
                border: 0 !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:first-child,
            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:last-child {
                display: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:nth-child(2) {
                flex: 0 0 min(815px, 46%) !important;
                width: min(815px, 46%) !important;
                max-width: 815px !important;
                padding: clamp(1.45rem, 2.2vw, 2rem) !important;
                border: 1px solid rgba(148, 163, 184, 0.12) !important;
                border-radius: 12px !important;
                background: rgba(15, 23, 42, 0.42) !important;
                box-shadow: 0 26px 68px rgba(2, 6, 23, 0.24) !important;
                backdrop-filter: blur(18px) !important;
                overflow: visible !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:nth-child(3) {
                flex: 1 1 auto !important;
                width: auto !important;
                max-width: none !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-visual {
                display: flex !important;
                min-height: 100% !important;
                height: 100% !important;
                flex-direction: column !important;
                justify-content: flex-end !important;
                padding: clamp(1.5rem, 3vw, 2.6rem) !important;
                border-radius: 24px !important;
                border: 1px solid rgba(20, 230, 176, 0.32) !important;
                background:
                    linear-gradient(145deg, rgba(20, 34, 54, 0.92), rgba(27, 40, 62, 0.90)),
                    radial-gradient(circle at 70% 20%, rgba(20, 230, 176, 0.15), transparent 20rem) !important;
                overflow: hidden !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-visual::after {
                content: "" !important;
                display: none !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-visual h2 {
                max-width: 680px !important;
                margin: 1.2rem 0 1rem !important;
                font-size: clamp(2.4rem, 4vw, 4.15rem) !important;
                line-height: 1.06 !important;
                font-weight: 860 !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-visual p {
                max-width: 620px !important;
                color: #dbeafe !important;
                -webkit-text-fill-color: #dbeafe !important;
                font-size: 1.02rem !important;
                line-height: 1.6 !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-preview-grid {
                display: grid !important;
                grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
                gap: 0.8rem !important;
                margin-top: 1.5rem !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-preview-grid > div {
                min-width: 0 !important;
                padding: 0.95rem !important;
                border-radius: 16px !important;
                border: 1px solid rgba(255, 255, 255, 0.14) !important;
                background: rgba(15, 23, 42, 0.42) !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-preview-grid span,
            .block-container:has(.runev-auth-page) .runev-auth-preview-grid b {
                display: block !important;
                color: #93c5fd !important;
                -webkit-text-fill-color: #93c5fd !important;
                font-size: 0.72rem !important;
                font-weight: 800 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.06em !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-preview-grid strong {
                display: block !important;
                margin: 0.3rem 0 !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 0.98rem !important;
                line-height: 1.25 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"],
            .block-container:has(.runev-auth-page) .runev-auth-divider {
                display: block !important;
                width: 100% !important;
                margin: 1rem 0 !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-divider {
                display: flex !important;
                align-items: center !important;
                gap: 0.95rem !important;
                color: #8ea0b8 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > a,
            .block-container:has(.runev-auth-page) .stButton > button,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button {
                width: 100% !important;
                min-width: 0 !important;
                min-height: 3.25rem !important;
                height: 3.25rem !important;
                border-radius: 15px !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
                font-size: 1rem !important;
                font-weight: 780 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > a {
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                border: 1px solid rgba(226, 232, 240, 0.24) !important;
                background: #f8fafc !important;
                color: #111827 !important;
                -webkit-text-fill-color: #111827 !important;
                box-shadow: none !important;
            }

            .block-container:has(.runev-auth-page) form {
                width: 100% !important;
                padding: 0 !important;
                border: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
                margin: 0 0 1.1rem !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] {
                display: flex !important;
                width: 100% !important;
                min-height: 3rem !important;
                height: auto !important;
                gap: 1.5rem !important;
                margin: 0.35rem 0 1.5rem !important;
                padding: 0 !important;
                border: 0 !important;
                border-bottom: 1px solid rgba(148, 163, 184, 0.14) !important;
                border-radius: 0 !important;
                background: transparent !important;
                overflow: visible !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button {
                flex: 0 1 auto !important;
                min-width: 0 !important;
                height: 3rem !important;
                min-height: 3rem !important;
                padding: 0 0.05rem !important;
                border: 0 !important;
                border-radius: 0 !important;
                background: transparent !important;
                color: #e5e7eb !important;
                -webkit-text-fill-color: #e5e7eb !important;
                font-size: 1rem !important;
                font-weight: 760 !important;
                white-space: nowrap !important;
                overflow: visible !important;
                text-overflow: clip !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button[aria-selected="true"] {
                background: transparent !important;
                border-bottom: 3px solid #ff3b5f !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [data-baseweb="tab-panel"] {
                padding: 1.2rem 1.45rem !important;
                border: 1px solid rgba(148, 163, 184, 0.10) !important;
                border-radius: 12px !important;
                background: rgba(15, 23, 42, 0.24) !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stVerticalBlock"] {
                gap: 0.65rem !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stForm"] {
                margin-bottom: 1rem !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input {
                width: 100% !important;
                min-width: 0 !important;
                height: 3.15rem !important;
                min-height: 3.15rem !important;
                border-radius: 12px !important;
                box-sizing: border-box !important;
            }

            .block-container:has(.runev-auth-page) .stCheckbox label {
                display: flex !important;
                align-items: center !important;
                gap: 0.55rem !important;
                line-height: 1.25 !important;
            }

            @media (max-width: 900px) {
                .block-container:has(.runev-auth-page) {
                    align-items: flex-start !important;
                    padding: 0.9rem !important;
                }

                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) {
                    width: 100% !important;
                    min-height: 0 !important;
                    flex-direction: column !important;
                }

                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:nth-child(2),
                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:nth-child(3) {
                    flex: 1 1 auto !important;
                    width: 100% !important;
                    max-width: 100% !important;
                }

                .block-container:has(.runev-auth-page) .runev-auth-visual {
                    min-height: 300px !important;
                }

                .block-container:has(.runev-auth-page) .runev-auth-preview-grid {
                    grid-template-columns: 1fr !important;
                }
            }

            /* Passenger deployed reference match. */
            .block-container:has(.runev-auth-page) {
                padding: 3.25rem 2rem 2rem !important;
                align-items: stretch !important;
                justify-content: flex-start !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-heading {
                width: 100% !important;
                max-width: none !important;
                min-height: 205px !important;
                margin: 0 0 1.55rem !important;
                padding: 2.05rem 2.15rem !important;
                border-radius: 30px !important;
                border: 1px solid rgba(148, 163, 184, 0.20) !important;
                background:
                    linear-gradient(90deg, rgba(14, 88, 82, 0.72) 0%, rgba(29, 47, 74, 0.76) 49%, rgba(31, 39, 53, 0.86) 100%) !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-heading span {
                font-size: 0.92rem !important;
                letter-spacing: 0.13em !important;
                margin-bottom: 0.65rem !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-main-title {
                max-width: none !important;
                font-size: clamp(2.8rem, 3vw, 3.55rem) !important;
                line-height: 1.08 !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-heading p {
                max-width: none !important;
                font-size: 1.05rem !important;
                line-height: 1.35 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) {
                width: 100% !important;
                max-width: none !important;
                min-height: 0 !important;
                gap: 1.45rem !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:nth-child(2) {
                flex: 0 0 calc(45.5% - 0.75rem) !important;
                width: calc(45.5% - 0.75rem) !important;
                max-width: calc(45.5% - 0.75rem) !important;
                padding: 0 !important;
                border: 0 !important;
                border-radius: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
                backdrop-filter: none !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:nth-child(3) {
                flex: 1 1 auto !important;
                width: auto !important;
                max-width: none !important;
            }

            .runev-user-auth-card {
                display: none !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] {
                gap: 1.6rem !important;
                min-height: 3rem !important;
                margin: 0 0 1.55rem !important;
                padding: 0 !important;
                border: 0 !important;
                border-bottom: 1px solid rgba(148, 163, 184, 0.12) !important;
                border-radius: 0 !important;
                background: transparent !important;
                overflow: visible !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button {
                flex: 0 0 auto !important;
                height: 3rem !important;
                min-height: 3rem !important;
                padding: 0 0.05rem !important;
                border-radius: 0 !important;
                color: #e5e7eb !important;
                -webkit-text-fill-color: #e5e7eb !important;
                font-size: 1rem !important;
                font-weight: 730 !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button[aria-selected="true"] {
                border-bottom: 3px solid #ff3b5f !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [data-baseweb="tab-panel"] {
                padding: 1.55rem 1.45rem !important;
                border: 1px solid rgba(148, 163, 184, 0.08) !important;
                border-radius: 10px !important;
                background: rgba(15, 23, 42, 0.16) !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput {
                margin-bottom: 1rem !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput label,
            .block-container:has(.runev-auth-page) .stCheckbox label {
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 0.96rem !important;
                font-weight: 720 !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input {
                height: 3.15rem !important;
                min-height: 3.15rem !important;
                border-radius: 12px !important;
                border: 1.5px solid rgba(241, 245, 249, 0.92) !important;
                background: rgba(71, 85, 105, 0.82) !important;
            }

            .block-container:has(.runev-auth-page) form {
                margin: 0 !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stForm"] {
                margin: 0 0 1.35rem !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] {
                margin: 0 0 1rem !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-divider {
                display: flex !important;
                margin: 0.45rem 0 1rem !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="stLinkButton"] > a,
            .block-container:has(.runev-auth-page) .stButton > button,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button {
                min-height: 3.25rem !important;
                height: 3.25rem !important;
                border-radius: 15px !important;
                font-size: 1rem !important;
                font-weight: 730 !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-visual {
                min-height: 535px !important;
                justify-content: flex-start !important;
                padding: 1.55rem 1.45rem !important;
                border-radius: 24px !important;
                border: 1px solid rgba(148, 163, 184, 0.18) !important;
                background: rgba(17, 24, 39, 0.76) !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-visual h2 {
                margin: 1.55rem 0 1.45rem !important;
                max-width: 100% !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: clamp(2.45rem, 3.05vw, 3.3rem) !important;
                line-height: 1.22 !important;
                font-weight: 840 !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-visual p {
                max-width: 100% !important;
                color: #f8fafc !important;
                -webkit-text-fill-color: #f8fafc !important;
                font-size: 1.05rem !important;
                line-height: 1.55 !important;
                font-weight: 650 !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-preview-grid {
                display: none !important;
            }

            .block-container:has(.runev-auth-page) .runev-auth-visual::after {
                content: "⚡" !important;
                display: block !important;
                margin-top: 4.2rem !important;
                margin-left: 2.1rem !important;
                color: #ff8a3d !important;
                font-size: 4.2rem !important;
                line-height: 1 !important;
                filter: drop-shadow(0 16px 24px rgba(251, 113, 133, 0.22)) !important;
            }

            @media (max-width: 900px) {
                .block-container:has(.runev-auth-page) {
                    padding: 1rem !important;
                }

                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) {
                    flex-direction: column !important;
                }

                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:nth-child(2),
                .block-container:has(.runev-auth-page) [data-testid="stHorizontalBlock"]:has(.runev-user-auth-card) > [data-testid="column"]:nth-child(3) {
                    flex: 1 1 auto !important;
                    width: 100% !important;
                    max-width: 100% !important;
                }
            }

            /* Exact screenshot-style auth page overrides */
            .block-container:has(.runev-auth-page),
            .block-container:has(.runev-driver-auth-page) {
                background: linear-gradient(135deg, rgba(8, 20, 31, 0.98), rgba(12, 20, 36, 0.98) 50%, rgba(16, 25, 43, 0.98)) !important;
            }

            .block-container:has(.runev-auth-page) [data-testid="column"]:has(.runev-auth-card-copy),
            .block-container:has(.runev-auth-page) [data-testid="column"]:nth-of-type(2),
            .block-container:has(.runev-driver-auth-page) [data-testid="column"]:has(.runev-driver-auth-copy),
            .block-container:has(.runev-driver-auth-page) [data-testid="column"]:nth-of-type(2) {
                background: rgba(15, 23, 42, 0.92) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                box-shadow: 0 30px 70px rgba(2, 6, 23, 0.30) !important;
                backdrop-filter: blur(18px) !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button,
            .block-container:has(.runev-driver-auth-page) .stTabs [role="tablist"] button {
                color: #cbd5e1 !important;
                background: transparent !important;
                border: none !important;
                border-bottom: 2px solid transparent !important;
            }

            .block-container:has(.runev-auth-page) .stTabs [role="tablist"] button[aria-selected="true"],
            .block-container:has(.runev-driver-auth-page) .stTabs [role="tablist"] button[aria-selected="true"] {
                color: #ffffff !important;
                border-bottom: 2px solid #14e6b0 !important;
                font-weight: 800 !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input,
            .block-container:has(.runev-driver-auth-page) .stTextInput input {
                min-height: 3rem !important;
                padding: 0.95rem 1rem !important;
                background: rgba(15, 23, 42, 0.96) !important;
                border: 1px solid rgba(255, 255, 255, 0.16) !important;
                border-radius: 16px !important;
                color: #f8fafc !important;
                box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.02) !important;
            }

            .block-container:has(.runev-auth-page) .stTextInput input::placeholder,
            .block-container:has(.runev-driver-auth-page) .stTextInput input::placeholder {
                color: rgba(248, 250, 252, 0.55) !important;
            }

            .block-container:has(.runev-auth-page) .stButton > button,
            .block-container:has(.runev-auth-page) .stFormSubmitButton > button,
            .block-container:has(.runev-driver-auth-page) .stButton > button,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button {
                min-height: 3rem !important;
                border-radius: 16px !important;
                background: linear-gradient(135deg, #14e6b0, #8175ff) !important;
                color: #ffffff !important;
                box-shadow: 0 20px 40px rgba(20, 230, 176, 0.18) !important;
            }

            .block-container:has(.runev-auth-page) .stFormSubmitButton > button:hover,
            .block-container:has(.runev-driver-auth-page) .stFormSubmitButton > button:hover {
                transform: translateY(-1px) !important;
                filter: brightness(1.06) !important;
            }

            .runev-auth-card-copy span,
            .runev-driver-auth-copy span {
                color: #14e6b0 !important;
            }

            .runev-auth-card-copy h2,
            .runev-driver-auth-copy h2 {
                color: #f8fafc !important;
            }

            .runev-auth-card-copy p,
            .runev-driver-auth-copy p {
                color: #cbd5e1 !important;
            }

            .runev-auth-legal {
                display: none !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    inject_sidebar_controller()


def inject_sidebar_controller() -> None:
    components.html(
        """
        <script>
        (() => {
            const doc = window.parent.document;
            const storageKey = "runev.sidebar.expanded";
            const buttonId = "runev-sidebar-float";
            const styleId = "runev-sidebar-controller-style";
            if (window.parent.__runevSidebarObserver) {
                try {
                    window.parent.__runevSidebarObserver.disconnect();
                } catch (_) {}
                window.parent.__runevSidebarObserver = null;
            }
            doc.getElementById(buttonId)?.remove();
            doc.getElementById(styleId)?.remove();
            return;
            let persistedState = null;
            try {
                persistedState = window.parent.localStorage.getItem(storageKey);
            } catch (_) {}

            if (!doc.getElementById(styleId)) {
                const style = doc.createElement("style");
                style.id = styleId;
                style.textContent = `
                    .runev-sidebar-float {
                        position: fixed;
                        left: 0.65rem;
                        top: 4.4rem;
                        z-index: 999999;
                        width: 2.65rem;
                        height: 2.65rem;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        border: 1px solid rgba(0, 229, 168, 0.48);
                        border-radius: 999px;
                        background: linear-gradient(135deg, #00e5a8, #3b82f6);
                        color: #03111f;
                        box-shadow: 0 18px 46px rgba(2, 6, 23, 0.34);
                        cursor: pointer;
                        font: 900 1.25rem/1 Inter, system-ui, sans-serif;
                        transition: transform 180ms ease, opacity 180ms ease, box-shadow 180ms ease;
                    }
                    .runev-sidebar-float:hover {
                        transform: translateX(2px) scale(1.03);
                        box-shadow: 0 22px 58px rgba(59, 130, 246, 0.36);
                    }
                    .runev-sidebar-float[hidden] {
                        display: none !important;
                    }
                    .runev-sidebar-float:focus-visible {
                        outline: 3px solid rgba(0, 229, 168, 0.74);
                        outline-offset: 3px;
                    }
                    @media (max-width: 768px) {
                        .runev-sidebar-float {
                            top: 3.85rem;
                            left: 0.55rem;
                            width: 2.85rem;
                            height: 2.85rem;
                        }
                    }
                `;
                doc.head.appendChild(style);
            }

            let button = doc.getElementById(buttonId);
            if (!button) {
                button = doc.createElement("button");
                button.id = buttonId;
                button.className = "runev-sidebar-float";
                button.type = "button";
                button.setAttribute("aria-label", "Expand sidebar navigation");
                button.setAttribute("title", "Expand sidebar");
                button.textContent = "›";
                doc.body.appendChild(button);
            }

            const clickNativeToggle = () => {
                const selectors = [
                    '[data-testid="collapsedControl"] button',
                    '[data-testid="collapsedControl"]',
                    '[data-testid="stSidebarCollapseButton"] button',
                    '[data-testid="stSidebarCollapseButton"]'
                ];
                for (const selector of selectors) {
                    const node = doc.querySelector(selector);
                    if (node instanceof HTMLElement) {
                        node.click();
                        return true;
                    }
                }
                return false;
            };

            const sidebarIsExpanded = () => {
                const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                if (!sidebar) {
                    return false;
                }
                const rect = sidebar.getBoundingClientRect();
                const style = window.parent.getComputedStyle(sidebar);
                return rect.width > 80 && rect.right > 40 && style.visibility !== "hidden";
            };

            let lastExpanded = null;
            const sync = () => {
                const expanded = sidebarIsExpanded();
                if (expanded === lastExpanded) {
                    return;
                }
                lastExpanded = expanded;
                const nextState = expanded ? "true" : "false";
                try {
                    if (window.parent.localStorage.getItem(storageKey) !== nextState) {
                        window.parent.localStorage.setItem(storageKey, nextState);
                    }
                } catch (_) {}
                if (button.hidden !== expanded) {
                    button.hidden = expanded;
                }
                if (button.getAttribute("aria-expanded") !== nextState) {
                    button.setAttribute("aria-expanded", nextState);
                }
            };

            button.onclick = () => {
                button.setAttribute("aria-busy", "true");
                clickNativeToggle();
                window.setTimeout(() => {
                    button.setAttribute("aria-busy", "false");
                    sync();
                }, 260);
            };
            button.onkeydown = (event) => {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    button.click();
                }
            };

            if (!window.parent.__runevSidebarClickBound) {
                window.parent.__runevSidebarClickBound = true;
                doc.addEventListener("click", (event) => {
                    const target = event.target instanceof Element ? event.target : null;
                    if (
                        target &&
                        (
                            target.closest('[data-testid="collapsedControl"]') ||
                            target.closest('[data-testid="stSidebarCollapseButton"]')
                        )
                    ) {
                        lastExpanded = null;
                        window.setTimeout(sync, 260);
                        window.setTimeout(sync, 700);
                    }
                }, true);
            }

            if (!window.parent.__runevSidebarRestored) {
                window.parent.__runevSidebarRestored = true;
                window.setTimeout(() => {
                    if (persistedState === "false" && sidebarIsExpanded()) {
                        clickNativeToggle();
                        lastExpanded = null;
                    }
                    if (persistedState === "true" && !sidebarIsExpanded()) {
                        clickNativeToggle();
                        lastExpanded = null;
                    }
                    window.setTimeout(sync, 280);
                }, 220);
            }

            window.setTimeout(sync, 50);
            window.setTimeout(sync, 350);
            window.setTimeout(sync, 1000);
        })();
        </script>
        """,
        height=0,
        width=0,
    )
