"""PDF summarization workspace: upload a PDF, extract its text, and
summarize it, with status messages that reflect real processing steps."""
from __future__ import annotations

import streamlit as st

from components.result_view import render_result
from services import pdf_service
from services.ai_service import AIServiceError
from services.pdf_service import PDFServiceError
from services.summarizer import SummarizationSettings, summarize
from utils.helpers import generate_short_title
from utils.session import add_history_entry
from utils.validators import validate_pdf_upload


def render_pdf_workspace(settings: SummarizationSettings) -> None:
    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        label_visibility="collapsed",
        help="Drag and drop a PDF file here, or click to browse.",
    )

    if uploaded_file is None:
        st.markdown(
            "<span class='sb-muted'>Upload a PDF to get started. SmartScribe AI works "
            "best with text-based PDFs (articles, reports, papers). Scanned or "
            "image-only PDFs require OCR, which is not currently supported.</span>",
            unsafe_allow_html=True,
        )
        return

    file_bytes = uploaded_file.getvalue()
    validation = validate_pdf_upload(len(file_bytes), uploaded_file.name)
    if not validation:
        st.error(validation.message)
        return

    cache_key = f"{uploaded_file.name}-{len(file_bytes)}"
    if st.session_state.get("pdf_cache_key") != cache_key:
        st.session_state["pdf_cache_key"] = cache_key
        st.session_state["pdf_extracted"] = None
        st.session_state["last_pdf_result"] = None

    if st.session_state.get("pdf_extracted") is None:
        with st.status("Extracting document text...", expanded=False) as status:
            try:
                extraction = pdf_service.extract_text_from_pdf(file_bytes)
            except PDFServiceError as exc:
                status.update(label="Extraction failed", state="error")
                st.error(str(exc))
                return
            status.update(label="Text extracted", state="complete")
        st.session_state["pdf_extracted"] = extraction
    else:
        extraction = st.session_state["pdf_extracted"]

    _render_file_summary(uploaded_file.name, len(file_bytes), extraction)

    generate_clicked = st.button("Summarize PDF", type="primary")

    if generate_clicked:
        _run_pdf_summary(extraction.text, uploaded_file.name, settings)

    result = st.session_state.get("last_pdf_result")
    if result:
        st.markdown("<hr class='sb-divider'/>", unsafe_allow_html=True)
        summary, takeaways, insights, title = result
        render_result(
            title=title,
            summary=summary,
            key_takeaways=takeaways,
            insights=insights,
            key_prefix="pdf",
        )


def _render_file_summary(filename: str, file_size_bytes: int, extraction) -> None:
    size_kb = file_size_bytes / 1024
    size_label = f"{size_kb / 1024:.1f} MB" if size_kb > 1024 else f"{size_kb:.0f} KB"
    approx_words = extraction.char_count // 5  # rough chars-per-word estimate

    metrics = [
        (filename, "Filename"),
        (str(extraction.page_count), "Pages"),
        (f"{approx_words:,}", "Extracted words (approx.)"),
        (size_label, "File size"),
    ]
    html = "<div class='sb-metric-grid'>"
    for value, label in metrics:
        html += (
            f"<div class='sb-metric'><div class='sb-metric-value' "
            f"style='font-size:1rem; word-break:break-word;'>{value}</div>"
            f"<div class='sb-metric-label'>{label}</div></div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _run_pdf_summary(text: str, filename: str, settings: SummarizationSettings) -> None:
    status_box = st.empty()

    def on_progress(message: str) -> None:
        status_box.info(message)

    try:
        result = summarize(text, settings, progress_callback=on_progress)
    except AIServiceError as exc:
        status_box.empty()
        st.error(str(exc))
        return
    except Exception:
        status_box.empty()
        st.error(
            "Something unexpected went wrong while generating the summary. Please try again."
        )
        return

    status_box.empty()

    title = generate_short_title(filename.rsplit(".", 1)[0].replace("_", " "))
    st.session_state["last_pdf_result"] = (
        result.summary,
        result.key_takeaways,
        result.insights,
        title,
    )
    add_history_entry(
        input_type="PDF",
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
