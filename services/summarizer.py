"""
Summarizer service — the application-layer orchestrator between the
Streamlit UI and the AI service.

This is the only place that decides *how* a request is fulfilled (a single
Gemini call vs. a map-reduce chunking pipeline) based on document length.
UI components never call `services.ai_service` directly — they call
`summarize()` here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from prompts.simplification import build_explain_simply_prompt, build_student_mode_prompt
from prompts.summarization import (
    build_chunk_summary_prompt,
    build_combine_prompt,
    build_summary_prompt,
)
from prompts.takeaways import build_key_takeaways_prompt
from services import ai_service
from services.text_processor import clean_text, needs_chunking, split_into_chunks
from utils.metrics import DocumentInsights, build_document_insights

MODE_SUMMARY = "Summary"
MODE_EXPLAIN_SIMPLY = "Explain Simply"
MODE_STUDENT_MODE = "Student Mode"
MODE_KEY_TAKEAWAYS = "Key Takeaways"

ALL_MODES = [MODE_SUMMARY, MODE_EXPLAIN_SIMPLY, MODE_STUDENT_MODE, MODE_KEY_TAKEAWAYS]

ProgressCallback = Optional[Callable[[str], None]]


@dataclass(frozen=True)
class SummarizationSettings:
    mode: str = MODE_SUMMARY
    length: str = "Medium"
    tone: str = "Neutral"
    output_format: str = "Paragraph"


@dataclass(frozen=True)
class SummarizationResult:
    summary: str
    key_takeaways: List[str]
    mode: str
    settings: SummarizationSettings
    insights: DocumentInsights
    was_chunked: bool
    chunk_count: int


def _report(callback: ProgressCallback, message: str) -> None:
    if callback:
        callback(message)


def summarize(
    text: str,
    settings: SummarizationSettings,
    progress_callback: ProgressCallback = None,
) -> SummarizationResult:
    """Run the full summarization pipeline for a piece of (already-validated) text."""
    _report(progress_callback, "Preparing document...")
    cleaned = clean_text(text)

    if needs_chunking(cleaned):
        summary, takeaways, chunk_count = _summarize_long_document(
            cleaned, settings, progress_callback
        )
        was_chunked = True
    else:
        _report(progress_callback, "Generating summary...")
        summary, takeaways = _summarize_single_pass(cleaned, settings)
        chunk_count = 1
        was_chunked = False

    _report(progress_callback, "Finalizing result...")
    insights = build_document_insights(cleaned, summary)

    return SummarizationResult(
        summary=summary,
        key_takeaways=takeaways,
        mode=settings.mode,
        settings=settings,
        insights=insights,
        was_chunked=was_chunked,
        chunk_count=chunk_count,
    )


def _build_single_pass_prompt(text: str, settings: SummarizationSettings) -> str:
    if settings.mode == MODE_EXPLAIN_SIMPLY:
        return build_explain_simply_prompt(text, settings.tone)
    if settings.mode == MODE_STUDENT_MODE:
        return build_student_mode_prompt(text)
    if settings.mode == MODE_KEY_TAKEAWAYS:
        return build_key_takeaways_prompt(text, settings.output_format)
    return build_summary_prompt(text, settings.length, settings.tone, settings.output_format)


def _summarize_single_pass(
    text: str, settings: SummarizationSettings
) -> Tuple[str, List[str]]:
    prompt = _build_single_pass_prompt(text, settings)
    response = ai_service.generate_structured(prompt)
    return response.summary, response.key_takeaways


def _summarize_long_document(
    text: str, settings: SummarizationSettings, progress_callback: ProgressCallback = None
) -> Tuple[str, List[str], int]:
    chunks = split_into_chunks(text)
    partial_summaries: List[str] = []

    for index, chunk in enumerate(chunks, start=1):
        _report(progress_callback, f"Analyzing section {index} of {len(chunks)}...")
        prompt = build_chunk_summary_prompt(chunk, index, len(chunks))
        partial_summaries.append(ai_service.generate_text(prompt))

    _report(progress_callback, "Generating final summary...")

    # For "Explain Simply" / "Student Mode" / "Key Takeaways" on long documents,
    # the reduce step still applies the mode-specific instructions, on top of the
    # already-condensed section summaries, so the final voice matches the mode.
    if settings.mode == MODE_EXPLAIN_SIMPLY:
        combined_source = "\n\n".join(partial_summaries)
        prompt = build_explain_simply_prompt(combined_source, settings.tone)
    elif settings.mode == MODE_STUDENT_MODE:
        combined_source = "\n\n".join(partial_summaries)
        prompt = build_student_mode_prompt(combined_source)
    elif settings.mode == MODE_KEY_TAKEAWAYS:
        combined_source = "\n\n".join(partial_summaries)
        prompt = build_key_takeaways_prompt(combined_source, settings.output_format)
    else:
        prompt = build_combine_prompt(
            partial_summaries, settings.length, settings.tone, settings.output_format
        )

    response = ai_service.generate_structured(prompt)
    return response.summary, response.key_takeaways, len(chunks)
