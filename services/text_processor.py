"""Text cleaning and chunking utilities, independent of any AI provider."""
from __future__ import annotations

import re
from typing import List

from utils.config import CHUNK_OVERLAP_CHARS, CHUNK_SIZE_CHARS, CHUNK_THRESHOLD_CHARS
from utils.metrics import count_words

_MULTI_SPACE = re.compile(r"[ \t]+")
_MULTI_NEWLINE = re.compile(r"\n{3,}")
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def clean_text(text: str) -> str:
    """Normalize whitespace and strip control characters from raw/extracted text."""
    if not text:
        return ""

    text = _CONTROL_CHARS.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _MULTI_SPACE.sub(" ", text)
    text = _MULTI_NEWLINE.sub("\n\n", text)
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    return text.strip()


def needs_chunking(text: str) -> bool:
    return len(text) > CHUNK_THRESHOLD_CHARS


def split_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE_CHARS,
    overlap: int = CHUNK_OVERLAP_CHARS,
) -> List[str]:
    """
    Split text into chunks close to `chunk_size` characters, preferring to break
    on paragraph boundaries (blank lines) and, failing that, sentence boundaries,
    so sentences are not cut mid-way whenever it's avoidable.
    """
    if not text or not text.strip():
        return []

    if len(text) <= chunk_size:
        return [text]

    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks: List[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        if len(paragraph) <= chunk_size:
            current = paragraph
        else:
            # A single paragraph is longer than chunk_size — split on sentences.
            chunks.extend(_split_long_paragraph(paragraph, chunk_size))
            current = ""

    if current:
        chunks.append(current)

    if overlap > 0 and len(chunks) > 1:
        chunks = _apply_overlap(chunks, overlap)

    return chunks


def _split_long_paragraph(paragraph: str, chunk_size: int) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    chunks: List[str] = []
    current = ""

    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)

        if len(sentence) <= chunk_size:
            current = sentence
        else:
            # Extremely long "sentence" with no punctuation — hard split.
            for i in range(0, len(sentence), chunk_size):
                chunks.append(sentence[i : i + chunk_size])
            current = ""

    if current:
        chunks.append(current)
    return chunks


def _apply_overlap(chunks: List[str], overlap: int) -> List[str]:
    overlapped = [chunks[0]]
    for i in range(1, len(chunks)):
        tail = chunks[i - 1][-overlap:]
        overlapped.append(f"{tail}\n\n{chunks[i]}")
    return overlapped


def word_count(text: str) -> int:
    """Thin re-export so callers working only with text_processor don't need
    to import utils.metrics directly."""
    return count_words(text)
