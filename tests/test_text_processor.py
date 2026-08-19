from services.text_processor import clean_text, split_into_chunks, word_count


def test_clean_text_normalizes_whitespace():
    raw = "Hello    world.\n\n\n\nThis  is   messy.\r\ntext"
    cleaned = clean_text(raw)
    assert "    " not in cleaned
    assert "\n\n\n" not in cleaned


def test_clean_text_handles_empty():
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_split_into_chunks_short_text_single_chunk():
    text = "This is a short piece of text."
    chunks = split_into_chunks(text, chunk_size=1000)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_split_into_chunks_respects_paragraph_boundaries():
    paragraph = "Sentence one. Sentence two. Sentence three. " * 5
    text = "\n\n".join([paragraph] * 6)
    chunks = split_into_chunks(text, chunk_size=400, overlap=0)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 500  # tolerance for paragraph-boundary grouping


def test_split_into_chunks_empty_text():
    assert split_into_chunks("") == []
    assert split_into_chunks("   ") == []


def test_split_into_chunks_overlap_adds_context():
    paragraph = "Sentence one. Sentence two. Sentence three. " * 5
    text = "\n\n".join([paragraph] * 6)
    chunks_no_overlap = split_into_chunks(text, chunk_size=400, overlap=0)
    chunks_with_overlap = split_into_chunks(text, chunk_size=400, overlap=50)
    assert len(chunks_with_overlap[1]) >= len(chunks_no_overlap[1])


def test_word_count_matches_metrics():
    text = "One two three four five"
    assert word_count(text) == 5
