from __future__ import annotations

import streamlit as st


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
                background: transparent !important;
                height: 2.75rem !important;
            }
            [data-testid="stDecoration"] { display: none; }
            [data-testid="stToolbar"] {
                visibility: visible !important;
                background: transparent !important;
            }
            [data-testid="collapsedControl"] {
                display: flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                z-index: 999999 !important;
            }

            .block-container {
                max-width: 1440px;
                padding: 0.2rem 1.6rem 3rem;
            }

            [data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, rgba(15, 23, 42, 0.97), rgba(30, 41, 59, 0.96)),
                    radial-gradient(circle at top, rgba(0, 229, 168, 0.16), transparent 18rem);
                border-right: 1px solid var(--runev-border);
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
        </style>
        """,
        unsafe_allow_html=True,
    )
