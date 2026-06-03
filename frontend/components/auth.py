from __future__ import annotations

import streamlit as st

from frontend.components.ui import safe_text


def render_auth_divider(label: str = "or") -> None:
    st.markdown(
        f"""
        <div class="runev-auth-divider" style="display:flex;align-items:center;gap:12px;margin:1rem 0;color:var(--runev-muted);font-weight:700;font-size:0.86rem;">
            <span style="height:1px;background:var(--runev-divider);flex:1"></span>
            <span>{safe_text(label)}</span>
            <span style="height:1px;background:var(--runev-divider);flex:1"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )
