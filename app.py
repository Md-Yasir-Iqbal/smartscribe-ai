"""
SmartScribe AI — application entry point.

This file only wires together page configuration, global styling, session
state, the sidebar, and page routing. All business logic lives in
services/, all prompt construction in prompts/, and all UI pieces in
components/ — app.py itself stays thin on purpose.
"""
from __future__ import annotations

import streamlit as st

from components.about import render_about
from components.header import inject_global_styles, render_page_title
from components.history_view import render_history
from components.home import render_home
from components.pdf_workspace import render_pdf_workspace
from components.sidebar import render_sidebar
from components.text_workspace import render_text_workspace
from utils.session import get_page, init_session_state

st.set_page_config(
    page_title="SmartScribe AI",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    init_session_state()
    inject_global_styles()

    settings = render_sidebar()
    page = get_page()

    if page == "Home":
        render_home()
    elif page == "Summarize Text":
        render_page_title(
            "Summarize Text", "Paste any text and generate a faithful, original summary."
        )
        render_text_workspace(settings)
    elif page == "Summarize PDF":
        render_page_title(
            "Summarize PDF", "Upload a PDF and let SmartScribe AI extract and summarize it."
        )
        render_pdf_workspace(settings)
    elif page == "History":
        render_page_title("History", "Results generated during this session.")
        render_history()
    elif page == "About":
        render_page_title("About SmartScribe AI", "How it works, and what to expect.")
        render_about()
    else:
        render_home()


if __name__ == "__main__":
    main()
