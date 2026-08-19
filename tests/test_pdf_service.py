import pymupdf as fitz
import pytest

from services.pdf_service import (
    PDFCorruptedError,
    PDFNoTextError,
    PDFPasswordProtectedError,
    extract_text_from_pdf,
)


def _make_pdf_bytes(text: str | None) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    if text:
        page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def test_extract_text_from_normal_pdf():
    pdf_bytes = _make_pdf_bytes(
        "This is a test document with enough readable text content to pass "
        "the extraction heuristic used by SmartScribe AI for detecting real text "
        "in an uploaded PDF file."
    )
    result = extract_text_from_pdf(pdf_bytes)
    assert result.page_count == 1
    assert "test document" in result.text.lower()
    assert result.char_count > 0


def test_extract_text_from_blank_pdf_raises_no_text_error():
    pdf_bytes = _make_pdf_bytes(None)
    with pytest.raises(PDFNoTextError):
        extract_text_from_pdf(pdf_bytes)


def test_extract_text_from_password_protected_pdf_raises():
    doc = fitz.open()
    doc.new_page()
    encrypted_bytes = doc.tobytes(
        encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw="owner", user_pw="secret123"
    )
    doc.close()

    with pytest.raises(PDFPasswordProtectedError):
        extract_text_from_pdf(encrypted_bytes)


def test_extract_text_from_corrupted_bytes_raises():
    with pytest.raises(PDFCorruptedError):
        extract_text_from_pdf(b"this is not a real pdf file at all")
