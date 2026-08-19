"""About page: what the app does, how it works, and honest capability notes."""
from __future__ import annotations

import streamlit as st

from utils.config import get_config


def render_about() -> None:
    st.markdown(
        "SmartScribe AI is an AI-powered text and PDF summarizer built with Streamlit "
        "and Google's Gemini API. It turns long articles, essays, research material, "
        "and PDF documents into clear, faithful summaries written in original wording "
        "— not copy-pasted excerpts."
    )

    st.markdown("<div class='sb-section-label'>How it works</div>", unsafe_allow_html=True)
    st.markdown(
        "1. Paste text, or upload a PDF.\n"
        "2. SmartScribe AI cleans the text and, if it's long, splits it into chunks.\n"
        "3. Each chunk is summarized, and long documents are combined into one final "
        "summary.\n"
        "4. Gemini generates a summary and key takeaways in the tone, length, and "
        "format you chose in the sidebar.\n"
        "5. Download or copy the result, or find it again later in History."
    )

    st.markdown("<div class='sb-section-label'>Processing modes</div>", unsafe_allow_html=True)
    st.markdown(
        "- **Summary** — combine with Length (Very Short → Detailed) and Format "
        "(Paragraph, Bullet Points, Numbered Points) for a Quick, Detailed, or "
        "Bullet-style summary.\n"
        "- **Explain Simply** — rewrites difficult material in plain language, "
        "explaining hard concepts rather than just trimming them.\n"
        "- **Student Mode** — explains the material the way a tutor would to someone "
        "learning it for the first time.\n"
        "- **Key Takeaways** — distills the most important standalone points."
    )

    st.markdown("<div class='sb-section-label'>Good to know</div>", unsafe_allow_html=True)
    st.markdown(
        "- Gemini's free tier is subject to Google's current rate limits and quotas, "
        "which can change over time — SmartScribe AI shows a clear message if a quota "
        "or rate limit is hit, rather than failing silently.\n"
        "- Scanned or image-only PDFs are not supported, since this app does not "
        "perform OCR.\n"
        "- History is stored only in your current browser session and clears when "
        "the session ends — no database is used."
    )

    st.markdown("<div class='sb-section-label'>Tech stack</div>", unsafe_allow_html=True)
    st.markdown("Python · Streamlit · Google Gemini API (`google-genai`) · PyMuPDF")

    config = get_config()
    st.caption(f"Configured Gemini model: `{config.gemini_model}`")
