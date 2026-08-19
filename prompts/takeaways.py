"""Prompt builder for the "Key Takeaways" processing mode."""
from __future__ import annotations

from prompts import FORMAT_GUIDE, JSON_OUTPUT_CONTRACT, ORIGINALITY_RULES


def build_key_takeaways_prompt(text: str, output_format: str) -> str:
    format_instruction = FORMAT_GUIDE.get(output_format, FORMAT_GUIDE["Paragraph"])

    return f"""You are an analyst distilling the most important ideas from a piece of text.

Task: Identify the most important concepts, findings, and conclusions in the SOURCE TEXT below.

For the "summary" field: write 1-2 sentences (structured as {format_instruction}) framing what
the text is about overall.
For the "key_takeaways" field: list the 4-6 most important, standalone takeaways a busy reader
must know. Each takeaway should be a complete, self-contained point, not a sentence fragment.

{ORIGINALITY_RULES}

{JSON_OUTPUT_CONTRACT}

SOURCE TEXT:
\"\"\"
{text}
\"\"\"
"""
