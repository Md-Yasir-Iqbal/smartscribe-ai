"""
Prompt builders for the standard "Summary" processing mode.

Also includes the map/reduce prompts used when a document is too long for a
single request: `build_chunk_summary_prompt` summarizes one chunk (the "map"
step) and `build_combine_prompt` merges the partial summaries into one final
summary (the "reduce" step).
"""
from __future__ import annotations

from typing import List

from prompts import FORMAT_GUIDE, JSON_OUTPUT_CONTRACT, LENGTH_GUIDE, ORIGINALITY_RULES, TONE_GUIDE


def build_summary_prompt(text: str, length: str, tone: str, output_format: str) -> str:
    length_instruction = LENGTH_GUIDE.get(length, LENGTH_GUIDE["Medium"])
    tone_instruction = TONE_GUIDE.get(tone, TONE_GUIDE["Neutral"])
    format_instruction = FORMAT_GUIDE.get(output_format, FORMAT_GUIDE["Paragraph"])

    return f"""You are an expert editor who writes clear, faithful summaries of source material.

Task: Summarize the SOURCE TEXT below.

Length: The summary should be {length_instruction}
Tone: Write in {tone_instruction}
Format: Structure the "summary" field as {format_instruction}

{ORIGINALITY_RULES}

{JSON_OUTPUT_CONTRACT}

SOURCE TEXT:
\"\"\"
{text}
\"\"\"
"""


def build_chunk_summary_prompt(chunk_text: str, chunk_index: int, total_chunks: int) -> str:
    return f"""You are summarizing part {chunk_index} of {total_chunks} of a longer document.
Write a faithful, condensed summary of ONLY this section in your own words. Preserve key facts,
numbers, names, and dates. Do not add information that is not in this section. Do not comment on
the fact that this is a partial section — just summarize its content directly.

Respond with plain text only (no JSON, no markdown headers) — just the summary paragraph(s).

SECTION {chunk_index} OF {total_chunks}:
\"\"\"
{chunk_text}
\"\"\"
"""


def build_combine_prompt(
    partial_summaries: List[str], length: str, tone: str, output_format: str
) -> str:
    length_instruction = LENGTH_GUIDE.get(length, LENGTH_GUIDE["Medium"])
    tone_instruction = TONE_GUIDE.get(tone, TONE_GUIDE["Neutral"])
    format_instruction = FORMAT_GUIDE.get(output_format, FORMAT_GUIDE["Paragraph"])

    joined = "\n\n".join(
        f"[Section {i + 1} summary]\n{s}" for i, s in enumerate(partial_summaries)
    )

    return f"""You are combining section-by-section summaries of a long document into one
cohesive final summary of the WHOLE document.

Length: The final summary should be {length_instruction}
Tone: Write in {tone_instruction}
Format: Structure the "summary" field as {format_instruction}

{ORIGINALITY_RULES}
- Merge overlapping or repeated points across sections instead of listing them multiple times.
- Present the ideas in a logical order, not necessarily the order the sections are listed in.

{JSON_OUTPUT_CONTRACT}

SECTION SUMMARIES:
{joined}
"""
