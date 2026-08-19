"""Sidebar: branding, navigation, summarization settings, and Gemini status."""
from __future__ import annotations

import streamlit as st

from services.summarizer import ALL_MODES, MODE_SUMMARY, SummarizationSettings
from utils.config import get_config
from utils.session import get_page, set_page

NAV_ITEMS = ["Home", "Summarize Text", "Summarize PDF", "History", "About"]

LENGTH_OPTIONS = ["Very Short", "Short", "Medium", "Detailed"]
TONE_OPTIONS = ["Simple", "Neutral", "Academic", "Friendly", "Professional"]
FORMAT_OPTIONS = ["Paragraph", "Bullet Points", "Numbered Points"]


def render_sidebar() -> SummarizationSettings:
    with st.sidebar:
        st.markdown(
            "<div class='sb-brand'><span class='sb-brand-mark'>S</span>SmartScribe AI</div>"
            "<div class='sb-tagline'>AI text &amp; PDF summarizer</div>",
            unsafe_allow_html=True,
        )

        current_page = get_page()
        selected_page = st.radio(
            "Navigate",
            NAV_ITEMS,
            index=NAV_ITEMS.index(current_page) if current_page in NAV_ITEMS else 0,
            label_visibility="collapsed",
        )
        if selected_page != current_page:
            set_page(selected_page)
            st.rerun()

        st.markdown("<div class='sb-section-label'>Settings</div>", unsafe_allow_html=True)

        mode = st.selectbox("Processing mode", ALL_MODES, index=0, key="setting_mode")
        length = st.select_slider(
            "Summary length",
            options=LENGTH_OPTIONS,
            value="Medium",
            key="setting_length",
            disabled=mode != MODE_SUMMARY,
            help="Only used in Summary mode.",
        )
        tone = st.selectbox("Tone", TONE_OPTIONS, index=1, key="setting_tone")
        output_format = st.selectbox(
            "Output format", FORMAT_OPTIONS, index=0, key="setting_format"
        )

        st.markdown("<div class='sb-section-label'>Status</div>", unsafe_allow_html=True)
        _render_gemini_status()

        st.caption("SmartScribe AI · v1.0")

    return SummarizationSettings(
        mode=mode, length=length, tone=tone, output_format=output_format
    )


def _render_gemini_status() -> None:
    config = get_config()
    if config.is_configured:
        st.markdown(
            "<span class='sb-pill sb-pill-ok'><span class='sb-pill-dot'></span>"
            "Gemini API &middot; Configured</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span class='sb-pill sb-pill-warn'><span class='sb-pill-dot'></span>"
            "Gemini API &middot; Not configured</span>",
            unsafe_allow_html=True,
        )
        st.caption("Add GEMINI_API_KEY to .env (local) or Streamlit Secrets (deployed).")
