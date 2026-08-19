from utils.metrics import (
    build_document_insights,
    compression_percentage,
    count_words,
    estimate_reading_minutes,
    format_reading_time,
)


def test_count_words_basic():
    assert count_words("Hello world, this is SmartScribe.") == 5


def test_count_words_empty():
    assert count_words("") == 0
    assert count_words(None) == 0


def test_estimate_reading_minutes():
    assert estimate_reading_minutes(200, wpm=200) == 1.0
    assert estimate_reading_minutes(0) == 0.0


def test_format_reading_time():
    assert format_reading_time(0) == "< 1 min read"
    assert format_reading_time(1.2) == "1 min read"
    assert format_reading_time(5.6) == "6 min read"


def test_compression_percentage():
    assert compression_percentage(100, 20) == 80.0
    assert compression_percentage(0, 10) == 0.0
    assert compression_percentage(100, 100) == 0.0


def test_compression_percentage_never_negative():
    # Summary longer than original should floor at 0%, not go negative.
    assert compression_percentage(10, 50) == 0.0


def test_build_document_insights():
    original = "word " * 100
    summary = "word " * 20
    insights = build_document_insights(original, summary)
    assert insights.original_word_count == 100
    assert insights.summary_word_count == 20
    assert insights.reduction_percentage == 80.0
    assert insights.time_saved_minutes >= 0
