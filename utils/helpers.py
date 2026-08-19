"""Small, generic helper functions used across the app."""
from __future__ import annotations

import re
from datetime import datetime
from typing import List


def generate_short_title(text: str, max_words: int = 8) -> str:
    if not text:
        return "Untitled"
    cleaned = re.sub(r"\s+", " ", text.strip())
    words = cleaned.split(" ")
    title = " ".join(words[:max_words])
    if len(words) > max_words:
        title += "..."
    return title or "Untitled"


def truncate(text: str, max_chars: int = 160) -> str:
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "..."


def timestamp_now() -> datetime:
    return datetime.now()


def format_timestamp(dt: datetime) -> str:
    return dt.strftime("%b %d, %Y - %I:%M %p")


def build_download_filename(base: str, extension: str) -> str:
    extension = extension.lstrip(".")
    return f"{base}.{extension}"


def result_to_markdown(title: str, summary: str, takeaways: List[str]) -> str:
    lines = [f"# {title}", "", "## Summary", "", summary, ""]
    if takeaways:
        lines.append("## Key Takeaways")
        lines.append("")
        for point in takeaways:
            lines.append(f"- {point}")
        lines.append("")
    lines.append("---")
    lines.append("_Generated with SmartScribe AI_")
    return "\n".join(lines)


def result_to_plain_text(title: str, summary: str, takeaways: List[str]) -> str:
    lines = [title, "=" * max(len(title), 1), "", "SUMMARY", "-" * 7, "", summary, ""]
    if takeaways:
        lines.append("KEY TAKEAWAYS")
        lines.append("-" * 13)
        lines.append("")
        for point in takeaways:
            lines.append(f"- {point}")
        lines.append("")
    lines.append("Generated with SmartScribe AI")
    return "\n".join(lines)
