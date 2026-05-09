from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Iterable

import plotly.graph_objects as go
import streamlit as st


def _get(row, name: str, default=None):
    if isinstance(row, dict):
        return row.get(name, default)
    return getattr(row, name, default)


def _date_label(value) -> str:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value[:10]
    if isinstance(value, datetime):
        return value.strftime("%d %b")
    return "Today"


def render_operations_analytics(requests: Iterable, providers: Iterable | None = None) -> None:
    rows = list(requests or [])
    providers = list(providers or [])
    revenue_by_day: dict[str, float] = defaultdict(float)
    trips_by_day: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    hour_counts: Counter[int] = Counter()
    units_by_day: dict[str, float] = defaultdict(float)

    for row in rows:
        label = _date_label(_get(row, "request_time"))
        amount = float(_get(row, "total_price", 0) or 0)
        units = float(_get(row, "charged_units_kwh", 0) or 0)
        revenue_by_day[label] += amount
        units_by_day[label] += units
        trips_by_day[label] += 1
        status_counts[_get(row, "status", "unknown")] += 1
        request_time = _get(row, "request_time")
        if isinstance(request_time, datetime):
            hour_counts[request_time.hour] += 1

    if not rows:
        st.info("Analytics will populate as trips, bills, and payments are created.")
        return

    days = list(trips_by_day.keys())
    revenue = [revenue_by_day[day] for day in days]
    trips = [trips_by_day[day] for day in days]
    units = [units_by_day[day] for day in days]

    col_a, col_b = st.columns(2)
    with col_a:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=revenue, mode="lines+markers", name="Revenue", line=dict(color="#00e5a8", width=4)))
        fig.update_layout(title="Revenue Trend", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.55)", height=330)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=days, y=trips, name="Trips", marker_color="#3b82f6"))
        fig.add_trace(go.Bar(x=days, y=units, name="kWh", marker_color="#00e5a8"))
        fig.update_layout(title="Daily Trips & Charging", template="plotly_dark", barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.55)", height=330)
        st.plotly_chart(fig, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        fig = go.Figure(data=[go.Pie(labels=list(status_counts.keys()), values=list(status_counts.values()), hole=0.62)])
        fig.update_traces(marker=dict(colors=["#00e5a8", "#3b82f6", "#f59e0b", "#ef4444", "#64748b"]))
        fig.update_layout(title="Trip Status Mix", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=320)
        st.plotly_chart(fig, use_container_width=True)
    with col_d:
        hours = list(range(24))
        values = [hour_counts.get(hour, 0) for hour in hours]
        fig = go.Figure(data=go.Heatmap(z=[values], x=[f"{hour:02d}:00" for hour in hours], y=["Demand"], colorscale=[[0, "#1e293b"], [1, "#00e5a8"]]))
        fig.update_layout(title="Peak Hours Heatmap", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=320)
        st.plotly_chart(fig, use_container_width=True)

    if providers:
        active = sum(1 for provider in providers if _get(provider, "is_available", False))
        st.caption(f"Driver activity: {active}/{len(providers)} vans currently available")

