from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from utils import api_client


THEME_OPTIONS = {
    "system": "System",
    "dark": "Dark",
    "light": "Light",
}


def init_theme_state(default: str = "system") -> None:
    st.session_state.setdefault("runev_theme_mode", default if default in THEME_OPTIONS else "system")


def current_theme() -> str:
    return st.session_state.get("runev_theme_mode", "system")


def apply_theme_runtime() -> None:
    theme = current_theme()
    components.html(
        f"""
        <script>
            const theme = {theme!r};
            const root = window.parent.document.documentElement;
            root.dataset.runevTheme = theme;
            window.parent.localStorage.setItem("runev.theme", theme);
        </script>
        """,
        height=0,
    )


def render_theme_selector(key: str = "runev_theme_selector") -> str:
    init_theme_state()
    active = current_theme()
    labels = list(THEME_OPTIONS.values())
    reverse = {label: value for value, label in THEME_OPTIONS.items()}
    selected = st.radio(
        "Theme",
        labels,
        index=labels.index(THEME_OPTIONS.get(active, "System")),
        horizontal=True,
        key=key,
    )
    mode = reverse[selected]
    st.session_state.runev_theme_mode = mode
    apply_theme_runtime()
    return mode


def restore_theme_preferences(token: str | None) -> dict | None:
    if not token:
        return None
    try:
        preferences = api_client.get_preferences(token)
    except api_client.ApiError:
        return None

    mode = preferences.get("theme_mode", "system")
    if mode in THEME_OPTIONS:
        st.session_state.runev_theme_mode = mode
        st.session_state.runev_theme_saved_mode = mode
        apply_theme_runtime()

    st.session_state.runev_theme_preferences = preferences
    return preferences


def persist_theme_preference(token: str | None, mode: str) -> bool:
    if not token or mode not in THEME_OPTIONS:
        return False
    if st.session_state.get("runev_theme_saved_mode") == mode:
        return True
    try:
        preferences = api_client.update_preferences(token, theme_mode=mode)
    except api_client.ApiError as exc:
        st.warning(f"Theme preference could not be saved: {exc}")
        return False

    st.session_state.runev_theme_preferences = preferences
    st.session_state.runev_theme_saved_mode = preferences.get("theme_mode", mode)
    return True
