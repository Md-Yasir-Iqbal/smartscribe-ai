from utils.validators import validate_pdf_upload, validate_text_input


def test_empty_text_is_invalid():
    assert not validate_text_input("")
    assert not validate_text_input("   ")


def test_none_text_is_invalid():
    assert not validate_text_input(None)


def test_too_short_text_is_invalid():
    result = validate_text_input("Hi")
    assert not result
    assert "short" in result.message.lower()


def test_valid_text_passes():
    text = "This is a perfectly reasonable piece of text to summarize. " * 3
    assert validate_text_input(text)


def test_too_long_text_is_invalid():
    text = "word " * 30000
    result = validate_text_input(text)
    assert not result
    assert "characters" in result.message.lower()


def test_pdf_upload_wrong_extension():
    result = validate_pdf_upload(1000, "document.docx")
    assert not result


def test_pdf_upload_empty_file():
    result = validate_pdf_upload(0, "document.pdf")
    assert not result


def test_pdf_upload_too_large():
    too_big = 25 * 1024 * 1024
    result = validate_pdf_upload(too_big, "document.pdf")
    assert not result


def test_pdf_upload_valid():
    result = validate_pdf_upload(1024 * 500, "document.pdf")
    assert result
