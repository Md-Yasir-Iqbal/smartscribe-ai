"""Session history: browse and reopen results generated earlier in this
session. No database is used — history lives entirely in st.session_state."""
from __future__ import annotations

import streamlit as st

from components.result_view import render_result
from utils.helpers import format_timestamp
from utils.metrics import build_document_insights
from utils.session import clear_history, get_history


def render_history() -> None:
    history = get_history()

    if not history:
        st.markdown(
            "<span class='sb-muted'>No results yet this session. Summarize some text "
            "or a PDF to see it appear here.</span>",
            unsafe_allow_html=True,
        )
        return

    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.markdown(
            f"<span class='sb-muted'>{len(history)} result(s) in this session.</span>",
            unsafe_allow_html=True,
        )
    with top_col2:
        if st.button("Clear history", use_container_width=True):
            clear_history()
            st.rerun()

    st.write("")

    for entry in history:
        label = f"{entry.title}  ·  {entry.input_type}  ·  {format_timestamp(entry.timestamp)}"
        with st.expander(label):
            st.markdown(
                f"<span class='sb-muted'>Mode: {entry.mode} &middot; "
                f"{entry.summary_word_count} summary words</span>",
                unsafe_allow_html=True,
            )
            st.write("")
            insights = build_document_insights(entry.original_text, entry.summary)
            render_result(
                title=entry.title,
                summary=entry.summary,
                key_takeaways=entry.key_takeaways,
                insights=insights,
                key_prefix=f"hist-{entry.id}",
            )
