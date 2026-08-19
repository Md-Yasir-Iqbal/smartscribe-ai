"""
Shared prompt-engineering constants used across all prompt builders.

Centralizing these keeps every processing mode consistent with the same
non-negotiable rules: preserve facts, avoid hallucination, and write in
original wording rather than copying the source (see README → "How It
Works" for the reasoning behind this).
"""

ORIGINALITY_RULES = """
Rewriting rules (follow strictly):
- Write entirely in your own words. Do not copy sentences or long phrases directly from the source text.
- Preserve the original meaning, key facts, numbers, dates, names, and technical terms exactly as given.
- Do not invent, assume, or add any fact, statistic, or claim that is not present in the source text.
- Do not include your own opinions or commentary.
- If the source text is ambiguous or incomplete, do not fill in the gaps with assumptions.
""".strip()

JSON_OUTPUT_CONTRACT = """
Respond with ONLY a valid JSON object (no markdown code fences, no commentary before or after) with exactly this shape:
{
  "summary": "the main written result as a single string, using the requested output format",
  "key_takeaways": ["short takeaway 1", "short takeaway 2", "..."]
}
"summary" must be plain text. If the output format is "Bullet Points" or "Numbered Points", represent each point on its own line inside the "summary" string, separated by newline characters, using "- " or "1. " prefixes as appropriate.
"key_takeaways" must contain between 3 and 6 short, standalone bullet points capturing the most important ideas.
""".strip()

LENGTH_GUIDE = {
    "Very Short": "1-2 short sentences, capturing only the single most essential point.",
    "Short": "a short paragraph of about 3-4 sentences.",
    "Medium": "a well-developed paragraph or two of about 6-9 sentences.",
    "Detailed": (
        "a comprehensive, multi-paragraph summary that stays significantly shorter "
        "than the source while covering all major points."
    ),
}

TONE_GUIDE = {
    "Simple": "very simple, plain, everyday language suitable for a general reader.",
    "Neutral": "a clear, neutral, objective tone.",
    "Academic": "a formal, precise, academic tone appropriate for scholarly work.",
    "Friendly": "a warm, approachable, conversational tone.",
    "Professional": "a polished, professional, business-appropriate tone.",
}

FORMAT_GUIDE = {
    "Paragraph": "flowing prose paragraphs (no bullet points).",
    "Bullet Points": "a clear bulleted list of concise points.",
    "Numbered Points": "a numbered list of concise points in logical order.",
}
