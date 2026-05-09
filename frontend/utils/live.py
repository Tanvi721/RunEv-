from __future__ import annotations

import html
import time

import streamlit as st


def auto_refresh(seconds: int = 10, enabled: bool = True) -> None:
    if not enabled:
        return
    key = "_runev_last_live_refresh"
    st.session_state.setdefault(key, time.time())
    st.caption("Live mode on - refresh manually when needed")


def push_notification(message: str, level: str = "info") -> None:
    st.session_state["_runev_live_notification"] = {"message": message, "level": level}
    st.toast(message)


def render_live_notification() -> None:
    notification = st.session_state.get("_runev_live_notification")
    if not notification:
        return
    message = html.escape(notification.get("message", ""))
    level = notification.get("level", "info")
    class_name = {
        "success": "runev-notification-success",
        "warning": "runev-notification-warning",
        "error": "runev-notification-error",
    }.get(level, "runev-notification-info")
    st.markdown(
        f"""
        <div class="runev-notification {class_name}">
            <div class="runev-notification-title">Live update</div>
            <div>{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def toast_for_status(status: str | None, key_prefix: str) -> None:
    if not status:
        return
    key = f"{key_prefix}_last_status"
    previous = st.session_state.get(key)
    if previous and previous != status:
        messages = {
            "accepted": "Driver accepted request",
            "en_route": "Charging van is in route",
            "arrived": "Charging van has reached you",
            "charging": "Charging started",
            "awaiting_payment": "Charging completed. Payment is ready",
            "completed": "Payment received",
            "cancelled": "Request was cancelled",
        }
        push_notification(messages.get(status, f"Status updated: {status.replace('_', ' ').title()}"), "success")
    st.session_state[key] = status
