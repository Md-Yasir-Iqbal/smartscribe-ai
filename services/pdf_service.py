"""
PDF Service — extracts clean, validated text from uploaded PDF files using
PyMuPDF (fitz).

This module never talks to the Gemini API; it only handles PDF I/O and text
extraction, so failure modes (corrupted files, password protection, scanned/
image-only PDFs) can be caught with clear, specific errors before anything
is sent to the AI service.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pymupdf as fitz  # PyMuPDF — "fitz" is the historical import name

from services.text_processor import clean_text
from utils.config import MAX_PDF_PAGES

# Below this average characters-per-page (and an absolute floor), a PDF is
# treated as having no meaningful extractable text (e.g. a scanned/image-only
# document that would require OCR).
_MIN_CHARS_PER_PAGE = 15
_MIN_ABSOLUTE_CHARS = 200


class PDFServiceError(Exception):
    """Base exception for PDF extraction failures. Message is user-facing."""


class PDFCorruptedError(PDFServiceError):
    pass


class PDFPasswordProtectedError(PDFServiceError):
    pass


class PDFNoTextError(PDFServiceError):
    pass


class PDFTooLargeError(PDFServiceError):
    pass


@dataclass(frozen=True)
class PDFExtractionResult:
    text: str
    page_count: int
    char_count: int
    warnings: List[str] = field(default_factory=list)


def extract_text_from_pdf(file_bytes: bytes) -> PDFExtractionResult:
    """Extract and clean text from PDF bytes, raising typed errors on failure."""
    try:
        document = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:  # PyMuPDF raises various errors for invalid files
        raise PDFCorruptedError(
            "This PDF couldn't be opened. It may be corrupted or not a valid PDF file."
        ) from exc

    try:
        if document.needs_pass:
            # Some PDFs are "protected" with an empty password — try that first.
            if not document.authenticate(""):
                raise PDFPasswordProtectedError(
                    "This PDF is password-protected. Please remove the password "
                    "and upload it again."
                )

        page_count = document.page_count
        if page_count == 0:
            raise PDFNoTextError("This PDF has no pages.")

        if page_count > MAX_PDF_PAGES:
            raise PDFTooLargeError(
                f"This PDF has {page_count} pages, which is more than the "
                f"{MAX_PDF_PAGES}-page limit SmartScribe AI currently supports."
            )

        raw_pages = [page.get_text("text") for page in document]
    finally:
        document.close()

    raw_text = "\n\n".join(raw_pages)
    text = clean_text(raw_text)

    if len(text) < _MIN_CHARS_PER_PAGE * page_count and len(text) < _MIN_ABSOLUTE_CHARS:
        raise PDFNoTextError(
            "No readable text could be extracted from this PDF. It looks like it may "
            "be a scanned document or contain only images. SmartScribe AI does not "
            "currently perform OCR (optical character recognition), so please upload "
            "a PDF with selectable text, or run OCR on this file first."
        )

    return PDFExtractionResult(text=text, page_count=page_count, char_count=len(text))
