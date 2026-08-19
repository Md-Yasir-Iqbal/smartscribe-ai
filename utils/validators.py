"""Input validation helpers for SmartScribe AI."""
from __future__ import annotations

from dataclasses import dataclass

from utils.config import MAX_PDF_SIZE_MB, MAX_TEXT_CHARS, MIN_TEXT_CHARS


@dataclass(frozen=True)
class ValidationResult:
    """Result of a validation check. Truthy when valid, falsy when invalid."""

    is_valid: bool
    message: str = ""

    def __bool__(self) -> bool:
        return self.is_valid


def validate_text_input(text: str) -> ValidationResult:
    """Validate pasted text before it is sent for summarization."""
    if text is None:
        return ValidationResult(False, "Please paste some text to summarize.")

    stripped = text.strip()

    if not stripped:
        return ValidationResult(False, "Please paste some text to summarize.")

    if len(stripped) < MIN_TEXT_CHARS:
        return ValidationResult(
            False,
            f"That's too short to summarize meaningfully. Please paste at least "
            f"{MIN_TEXT_CHARS} characters (a sentence or two).",
        )

    if len(stripped) > MAX_TEXT_CHARS:
        return ValidationResult(
            False,
            f"That's a lot of text ({len(stripped):,} characters). SmartScribe AI "
            f"currently supports up to {MAX_TEXT_CHARS:,} characters of pasted text. "
            f"For longer documents, try the PDF Summarizer instead.",
        )

    return ValidationResult(True)


def validate_pdf_upload(file_size_bytes: int, filename: str) -> ValidationResult:
    """Validate an uploaded PDF's basic properties before extraction."""
    if not filename.lower().endswith(".pdf"):
        return ValidationResult(False, "Please upload a file in PDF format (.pdf).")

    if file_size_bytes == 0:
        return ValidationResult(False, "This file appears to be empty.")

    max_bytes = MAX_PDF_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        size_mb = file_size_bytes / (1024 * 1024)
        return ValidationResult(
            False,
            f"This PDF is {size_mb:.1f} MB, which is larger than the "
            f"{MAX_PDF_SIZE_MB} MB limit. Please upload a smaller file.",
        )

    return ValidationResult(True)
