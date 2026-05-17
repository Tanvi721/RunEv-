from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_component = components.declare_component(
    "runev_geolocation",
    path=str(Path(__file__).parent / "geolocation_component"),
)


def live_location_button(label: str = "Use My Live Location", key: str | None = None) -> dict[str, Any] | None:
    return _component(label=label, key=key, default=None)
