"""Reusable header / global-styling components."""
from __future__ import annotations

import os
from typing import Optional

import streamlit as st

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CSS_PATH = os.path.join(_PROJECT_ROOT, "assets", "style.css")


def inject_global_styles() -> None:
    """Load and inject the app's custom stylesheet, once per render."""
    try:
        with open(_CSS_PATH, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # The app still works with default Streamlit styling if the
        # stylesheet is ever missing — this should never happen in a normal
        # checkout, but we never want a missing asset to crash the app.
        pass


def render_page_title(title: str, subtitle: Optional[str] = None) -> None:
    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f"<p class='sb-muted'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown("<hr class='sb-divider'/>", unsafe_allow_html=True)
