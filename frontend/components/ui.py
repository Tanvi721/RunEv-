from __future__ import annotations

import html
from typing import Iterable

import streamlit as st


STATUS_COLORS = {
    "pending": "warn",
    "accepted": "blue",
    "en_route": "blue",
    "arrived": "blue",
    "charging": "green",
    "awaiting_payment": "warn",
    "completed": "green",
    "cancelled": "red",
    "rejected": "red",
    "online": "green",
    "offline": "warn",
}


def money(value: float | int | None) -> str:
    return f"Rs {float(value or 0):,.0f}"


def safe_text(value: object) -> str:
    return html.escape(str(value if value is not None else ""))


def hero(eyebrow: str, title: str, subtitle: str = "", right: str = "") -> None:
    st.markdown(
        f"""
        <div class="runev-hero">
            <div>
                <div class="runev-eyebrow">{safe_text(eyebrow)}</div>
                <div class="runev-title">{safe_text(title)}</div>
                <div class="runev-subtitle">{safe_text(subtitle)}</div>
            </div>
            <div>{right}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str | int | float, icon: str, delta: str = "") -> None:
    st.markdown(
        f"""
        <div class="runev-card runev-metric">
            <div class="runev-metric-icon">{icon}</div>
            <div class="runev-metric-label">{safe_text(label)}</div>
            <div class="runev-metric-value">{safe_text(value)}</div>
            <div class="runev-metric-delta">{safe_text(delta)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: str | None, label: str | None = None) -> str:
    normalized = (status or "unknown").lower()
    color = STATUS_COLORS.get(normalized, "blue")
    display = label or normalized.replace("_", " ").title()
    return f'<span class="runev-badge badge-{color}">{safe_text(display)}</span>'


def card_start(extra_class: str = "") -> None:
    st.markdown(f'<div class="runev-card {extra_class}">', unsafe_allow_html=True)


def card_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def timeline(current_status: str | None) -> None:
    steps = [
        ("pending", "Requested"),
        ("accepted", "Driver Assigned"),
        ("en_route", "Driver Reached"),
        ("charging", "Charging Started"),
        ("awaiting_payment", "Payment Pending"),
        ("completed", "Paid"),
    ]
    status = current_status or "pending"
    status_aliases = {
        "arrived": "en_route",
        "completed": "completed",
    }
    status = status_aliases.get(status, status)
    current_index = next((i for i, (key, _) in enumerate(steps) if key == status), 0)
    paid = status == "completed"
    rendered = []
    for index, (key, label) in enumerate(steps):
        cls = "runev-step-done" if index < current_index or paid else "runev-step-active" if index == current_index else ""
        marker = "&#10003;" if index < current_index or paid else "&#9675;"
        rendered.append(
            f'<span class="runev-step {cls}"><span class="runev-step-dot">{marker}</span>{safe_text(label)}</span>'
        )
    progress = 100 if paid else 0 if len(steps) == 1 else round((current_index / (len(steps) - 1)) * 100, 2)
    st.markdown(
        f'<div class="runev-timeline-wrap"><div class="runev-timeline-line"><span style="width:{progress}%"></span></div><div class="runev-timeline">{"".join(rendered)}</div></div>',
        unsafe_allow_html=True,
    )


def skeleton_grid(count: int = 3) -> None:
    cols = st.columns(count)
    for col in cols:
        with col:
            st.markdown('<div class="runev-skeleton"></div>', unsafe_allow_html=True)


def sidebar_nav(title: str, items: Iterable[tuple[str, str]], key: str) -> str:
    with st.sidebar:
        st.markdown(f"## {title}")
        st.caption("Premium EV operations console")
        item_map = {f"{icon}  {label}": label for icon, label in items}
        current = st.radio(
            "Navigation",
            list(item_map.keys()),
            key=key,
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("Live-ready modules: AI ETA, smart dispatch, battery intelligence, demand forecasting")
    return item_map[current]
