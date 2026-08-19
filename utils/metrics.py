"""Text metrics: word counts, reading time, and compression statistics.

Every value produced here is calculated directly from real input/output
text — nothing is fabricated or hard-coded.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from utils.config import READING_WPM

_WORD_PATTERN = re.compile(r"\b[\w'-]+\b", re.UNICODE)


def count_words(text: str) -> int:
    if not text:
        return 0
    return len(_WORD_PATTERN.findall(text))


def count_characters(text: str) -> int:
    return len(text) if text else 0


def estimate_reading_minutes(word_count: int, wpm: int = READING_WPM) -> float:
    if word_count <= 0 or wpm <= 0:
        return 0.0
    return word_count / wpm


def format_reading_time(minutes: float) -> str:
    if minutes <= 0:
        return "< 1 min read"
    total_minutes = max(1, round(minutes))
    return f"{total_minutes} min read"


def compression_percentage(original_words: int, summary_words: int) -> float:
    """Percentage reduction in word count, floored at 0 (never negative)."""
    if original_words <= 0:
        return 0.0
    reduction = 1 - (summary_words / original_words)
    return max(0.0, round(reduction * 100, 1))


@dataclass(frozen=True)
class DocumentInsights:
    original_word_count: int
    summary_word_count: int
    reduction_percentage: float
    original_reading_minutes: float
    summary_reading_minutes: float
    time_saved_minutes: float

    @property
    def original_reading_time_label(self) -> str:
        return format_reading_time(self.original_reading_minutes)

    @property
    def summary_reading_time_label(self) -> str:
        return format_reading_time(self.summary_reading_minutes)

    @property
    def time_saved_label(self) -> str:
        if self.time_saved_minutes < 1:
            return "< 1 min"
        return f"{round(self.time_saved_minutes)} min"


def build_document_insights(original_text: str, summary_text: str) -> DocumentInsights:
    """Compute all Document Insights metrics from real original/summary text."""
    original_words = count_words(original_text)
    summary_words = count_words(summary_text)
    original_minutes = estimate_reading_minutes(original_words)
    summary_minutes = estimate_reading_minutes(summary_words)

    return DocumentInsights(
        original_word_count=original_words,
        summary_word_count=summary_words,
        reduction_percentage=compression_percentage(original_words, summary_words),
        original_reading_minutes=original_minutes,
        summary_reading_minutes=summary_minutes,
        time_saved_minutes=max(0.0, original_minutes - summary_minutes),
    )
