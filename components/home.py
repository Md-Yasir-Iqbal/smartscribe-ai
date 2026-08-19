"""Landing / dashboard page."""
from __future__ import annotations

import streamlit as st

from utils.session import set_page

FEATURES = [
    ("Aa", "AI Summarization", "Turn long content into concise, faithful explanations."),
    ("Pdf", "PDF Intelligence", "Extract and summarize information straight from documents."),
    ("Ex", "Simple Explanations", "Convert difficult material into understandable language."),
    ("Kt", "Key Takeaways", "Quickly identify the most important ideas in any text."),
]


def render_home() -> None:
    st.markdown("<div class='sb-hero'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sb-hero-eyebrow'>AI Text &amp; PDF Summarizer</div>"
        "<h1>Turn complex information into "
        "<span class='sb-highlight'>clear ideas</span>.</h1>"
        "<p class='sb-subtitle'>Summarize, simplify, and understand text and documents "
        "with AI, powered by Google Gemini.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Summarize Text", type="primary", use_container_width=True):
            set_page("Summarize Text")
            st.rerun()
    with col2:
        if st.button("Summarize PDF", use_container_width=True):
            set_page("Summarize PDF")
            st.rerun()

    st.write("")
    st.write("")
    st.markdown("<div class='sb-section-label'>What it does</div>", unsafe_allow_html=True)

    cols = st.columns(4)
    for col, (icon, title, description) in zip(cols, FEATURES):
        with col:
            with st.container(border=True):
                st.markdown(f"<div class='sb-feature-icon'>{icon}</div>", unsafe_allow_html=True)
                st.markdown(f"**{title}**")
                st.markdown(f"<span class='sb-muted'>{description}</span>", unsafe_allow_html=True)
