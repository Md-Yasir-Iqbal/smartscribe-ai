"""Renders a summarization result: summary, key takeaways, document insights,
and export actions (copy / download). Reused by the text workspace, the PDF
workspace, and the history view so every result looks and behaves the same."""
from __future__ import annotations

import json
from typing import List

import streamlit as st
import streamlit.components.v1 as components

from utils.helpers import build_download_filename, result_to_markdown, result_to_plain_text
from utils.metrics import DocumentInsights


def render_result(
    *,
    title: str,
    summary: str,
    key_takeaways: List[str],
    insights: DocumentInsights,
    key_prefix: str,
) -> None:
    st.markdown("<div class='sb-section-label'>Summary</div>", unsafe_allow_html=True)
    st.write(summary)

    if key_takeaways:
        st.markdown("<div class='sb-section-label'>Key Takeaways</div>", unsafe_allow_html=True)
        for point in key_takeaways:
            st.markdown(f"- {point}")

    st.markdown("<div class='sb-section-label'>Document Insights</div>", unsafe_allow_html=True)
    _render_insights(insights)

    st.write("")
    _render_actions(title, summary, key_takeaways, key_prefix)


def _render_insights(insights: DocumentInsights) -> None:
    metrics = [
        (f"{insights.original_word_count:,}", "Original words"),
        (f"{insights.summary_word_count:,}", "Summary words"),
        (f"{insights.reduction_percentage:.0f}%", "Reduction"),
        (insights.time_saved_label, "Time saved"),
    ]
    html = "<div class='sb-metric-grid'>"
    for value, label in metrics:
        html += (
            f"<div class='sb-metric'><div class='sb-metric-value'>{value}</div>"
            f"<div class='sb-metric-label'>{label}</div></div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _render_actions(title: str, summary: str, key_takeaways: List[str], key_prefix: str) -> None:
    col1, col2, col3 = st.columns(3)

    md_content = result_to_markdown(title, summary, key_takeaways)
    txt_content = result_to_plain_text(title, summary, key_takeaways)

    with col1:
        _copy_button(txt_content, key=f"{key_prefix}-copy")
    with col2:
        st.download_button(
            "Download TXT",
            data=txt_content,
            file_name=build_download_filename("smartscribe_summary", "txt"),
            mime="text/plain",
            use_container_width=True,
            key=f"{key_prefix}-dl-txt",
        )
    with col3:
        st.download_button(
            "Download Markdown",
            data=md_content,
            file_name=build_download_filename("smartscribe_summary", "md"),
            mime="text/markdown",
            use_container_width=True,
            key=f"{key_prefix}-dl-md",
        )


def _copy_button(text: str, key: str) -> None:
    """A real clipboard-copy button, implemented with a small embedded script
    (Streamlit's st.markdown does not execute <script> tags, so this uses
    st.components.v1.html, which renders in a sandboxed iframe that does)."""
    safe_text = json.dumps(text)
    components.html(
        f"""
        <div style="font-family: Inter, -apple-system, sans-serif;">
          <button id="btn-{key}" style="width:100%; padding: 0.5rem 0.9rem; border-radius: 8px;
            border: 1px solid #E4E1D8; background: #FFFFFF; color: #14213D; font-weight: 600;
            cursor: pointer; font-size: 0.85rem;">
            Copy to clipboard
          </button>
          <div id="msg-{key}" style="margin-top: 0.3rem; color: #2F6F63; font-size: 0.78rem;
            text-align:center; min-height: 1em;"></div>
        </div>
        <script>
        const b = document.getElementById("btn-{key}");
        b.addEventListener("click", () => {{
          navigator.clipboard.writeText({safe_text}).then(() => {{
            document.getElementById("msg-{key}").innerText = "Copied!";
            setTimeout(() => {{ document.getElementById("msg-{key}").innerText = ""; }}, 1500);
          }});
        }});
        </script>
        """,
        height=70,
    )
