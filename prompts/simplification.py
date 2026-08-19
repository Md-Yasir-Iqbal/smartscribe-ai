"""Prompt builders for the "Explain Simply" and "Student Mode" processing modes."""
from __future__ import annotations

from prompts import JSON_OUTPUT_CONTRACT, ORIGINALITY_RULES, TONE_GUIDE


def build_explain_simply_prompt(text: str, tone: str) -> str:
    tone_instruction = TONE_GUIDE.get(tone, TONE_GUIDE["Simple"])

    return f"""You are a skilled teacher who explains difficult material in plain, accessible
language without dumbing down the substance.

Task: Rewrite the SOURCE TEXT so it is easy to understand for a general adult reader with no
background in the subject.

Do this properly:
- Do not simply delete "hard" words. Actually EXPLAIN any difficult concept, term, or idea in
  simple language, as if explaining it to a curious friend.
- Use short sentences and everyday vocabulary.
- Use a concrete example or analogy only where it genuinely helps understanding, and only if it
  does not introduce information that isn't implied by the source.
- Keep an overall tone that is {tone_instruction}

{ORIGINALITY_RULES}

{JSON_OUTPUT_CONTRACT}

SOURCE TEXT:
\"\"\"
{text}
\"\"\"
"""


def build_student_mode_prompt(text: str) -> str:
    return f"""You are a patient, encouraging tutor helping a student understand their study
material for the first time.

Task: Explain the SOURCE TEXT below the way a great tutor would explain it to a student who is
learning this topic for the first time.

Do this:
- Break the material into clear, logically ordered points.
- Define any technical term the first time you use it, in simple language.
- Explain WHY things matter or how ideas connect, not just WHAT they say.
- Keep the tone encouraging, clear, and student-friendly (but not childish).

{ORIGINALITY_RULES}

{JSON_OUTPUT_CONTRACT}

SOURCE TEXT:
\"\"\"
{text}
\"\"\"
"""
