"""Text summarization workspace: paste text, generate a summary using the
sidebar's settings, and view the result — all in a two-column layout."""
from __future__ import annotations

import streamlit as st

from components.result_view import render_result
from services.ai_service import AIServiceError
from services.summarizer import SummarizationSettings, summarize
from utils.helpers import generate_short_title
from utils.metrics import count_characters, count_words
from utils.session import add_history_entry
from utils.validators import validate_text_input

EXAMPLE_TEXT = (
    "Photosynthesis is the process by which green plants, algae, and some bacteria "
    "convert light energy, usually from the sun, into chemical energy stored in glucose. "
    "The process takes place mainly in the chloroplasts of plant cells, using a pigment "
    "called chlorophyll that absorbs light, particularly in the blue and red wavelengths, "
    "while reflecting green light, which is why most plants appear green. During "
    "photosynthesis, carbon dioxide from the air and water absorbed by the roots are "
    "combined using light energy to produce glucose and oxygen. The overall reaction can "
    "be summarized as six molecules of carbon dioxide plus six molecules of water, in the "
    "presence of light energy, yielding one molecule of glucose and six molecules of "
    "oxygen. This oxygen is released into the atmosphere as a byproduct, while the glucose "
    "is used by the plant for energy and growth, or stored for later use. Photosynthesis "
    "is essential to almost all life on Earth because it is the primary source of oxygen "
    "in the atmosphere and forms the base of most food chains, converting solar energy "
    "into a form that other organisms can consume and use."
)


def render_text_workspace(settings: SummarizationSettings) -> None:
    if "text_input_value" not in st.session_state:
        st.session_state["text_input_value"] = ""

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("<div class='sb-section-label'>Input</div>", unsafe_allow_html=True)

        button_col1, button_col2 = st.columns(2)
        with button_col1:
            if st.button("Use example text", use_container_width=True):
                st.session_state["text_input_value"] = EXAMPLE_TEXT
        with button_col2:
            if st.button("Clear", use_container_width=True):
                st.session_state["text_input_value"] = ""

        text = st.text_area(
            "Paste your text",
            value=st.session_state["text_input_value"],
            height=380,
            key="text_input_area",
            label_visibility="collapsed",
            placeholder="Paste an article, essay, research excerpt, or any long text here...",
        )
        st.session_state["text_input_value"] = text

        words = count_words(text)
        chars = count_characters(text)
        st.markdown(
            f"<span class='sb-muted'>{words:,} words &middot; {chars:,} characters</span>",
            unsafe_allow_html=True,
        )

        generate_clicked = st.button("Generate Summary", type="primary", use_container_width=True)

    with right:
        st.markdown("<div class='sb-section-label'>Result</div>", unsafe_allow_html=True)

        if generate_clicked:
            validation = validate_text_input(text)
            if not validation:
                st.error(validation.message)
            else:
                _run_summary(text, settings)

        result = st.session_state.get("last_text_result")
        if result:
            summary, takeaways, insights, title = result
            render_result(
                title=title,
                summary=summary,
                key_takeaways=takeaways,
                insights=insights,
                key_prefix="text",
            )
        else:
            st.markdown(
                "<span class='sb-muted'>Your generated summary will appear here.</span>",
                unsafe_allow_html=True,
            )


def _run_summary(text: str, settings: SummarizationSettings) -> None:
    with st.spinner("Analyzing and summarizing your text..."):
        try:
            result = summarize(text, settings)
        except AIServiceError as exc:
            st.error(str(exc))
            return
        except Exception:
            st.error(
                "Something unexpected went wrong while generating the summary. "
                "Please try again."
            )
            return

    title = generate_short_title(text)
    st.session_state["last_text_result"] = (
        result.summary,
        result.key_takeaways,
        result.insights,
        title,
    )
    add_history_entry(
        input_type="Text",
        summary=result.summary,
        key_takeaways=result.key_takeaways,
        mode=result.mode,
        original_text=text,
        source_title=title,
        settings={
            "length": settings.length,
            "tone": settings.tone,
            "format": settings.output_format,
            "mode": settings.mode,
        },
    )
    st.success("Summary generated.")
