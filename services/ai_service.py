"""
AI Service — the ONLY module in SmartScribe AI that talks to the Gemini API.

Responsibilities:
- Initialize and cache the Gemini client
- Submit prompts and extract responses (plain text or structured JSON)
- Classify and wrap SDK/network errors (invalid key, quota, rate limit,
  timeout, server errors, empty response) into friendly, typed exceptions
  the UI layer can catch and display

No Streamlit UI code lives here, and no prompt text is constructed here —
prompt construction lives entirely in the `prompts/` package. The intended
call chain is:

    Streamlit UI  ->  services/summarizer.py  ->  services/ai_service.py  ->  Gemini API
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import List

import streamlit as st
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from utils.config import get_config

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_MS = 60_000
DEFAULT_TEMPERATURE = 0.3


class AIServiceError(Exception):
    """Base exception for all AI service failures. Message is user-facing."""


class AINotConfiguredError(AIServiceError):
    pass


class AIInvalidKeyError(AIServiceError):
    pass


class AIQuotaExceededError(AIServiceError):
    pass


class AIRateLimitError(AIServiceError):
    pass


class AITimeoutError(AIServiceError):
    pass


class AIEmptyResponseError(AIServiceError):
    pass


@dataclass(frozen=True)
class StructuredAIResponse:
    summary: str
    key_takeaways: List[str]


@st.cache_resource(show_spinner=False)
def _get_client(api_key: str) -> "genai.Client":
    """Create (and cache) a single Gemini client for the app process."""
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
    )


def _build_client() -> "genai.Client":
    config = get_config()
    if not config.is_configured:
        raise AINotConfiguredError(
            "Gemini API key is not configured. Add GEMINI_API_KEY to your .env file "
            "(local development) or to Streamlit Secrets (deployed app)."
        )
    return _get_client(config.gemini_api_key)


def _classify_error(exc: Exception) -> AIServiceError:
    """Turn a raw SDK/network exception into a friendly, typed AIServiceError."""
    code = getattr(exc, "code", None)
    message = getattr(exc, "message", None) or str(exc)
    lowered = message.lower()

    if code in (401, 403) or "api key not valid" in lowered or "permission denied" in lowered:
        return AIInvalidKeyError(
            "Your Gemini API key was rejected. Please check that GEMINI_API_KEY is "
            "set correctly and hasn't been revoked."
        )

    if "quota" in lowered:
        return AIQuotaExceededError(
            "You've hit the Gemini API's usage quota. This can happen on the free "
            "tier — please wait a while and try again, or check your quota in "
            "Google AI Studio."
        )

    if code == 429 or "rate limit" in lowered or "resource_exhausted" in lowered:
        return AIRateLimitError(
            "SmartScribe AI is sending requests too quickly for Gemini's current "
            "rate limit. Please wait a few seconds and try again."
        )

    if "timeout" in lowered or "deadline" in lowered or isinstance(exc, TimeoutError):
        return AITimeoutError(
            "The request to Gemini took too long and timed out. Please try again, "
            "or try with a shorter document."
        )

    if code is not None:
        try:
            if 500 <= int(code) < 600:
                return AIServiceError(
                    "Gemini's servers are temporarily having issues. Please try "
                    "again in a moment."
                )
        except (TypeError, ValueError):
            pass

    return AIServiceError(
        "Something went wrong while talking to the Gemini API. Please try again."
    )


def _extract_text(response) -> str:
    try:
        text = response.text
    except Exception:
        text = None
    return (text or "").strip()


def generate_text(prompt: str, *, temperature: float = DEFAULT_TEMPERATURE) -> str:
    """Send a plain-text prompt to Gemini and return the plain-text response."""
    client = _build_client()
    config = get_config()

    try:
        response = client.models.generate_content(
            model=config.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=temperature),
        )
    except genai_errors.APIError as exc:
        logger.warning("Gemini API error: %s", exc)
        raise _classify_error(exc) from exc
    except Exception as exc:  # network errors, timeouts, etc.
        logger.warning("Unexpected error calling Gemini: %s", exc)
        raise _classify_error(exc) from exc

    text = _extract_text(response)
    if not text:
        raise AIEmptyResponseError("Gemini returned an empty response. Please try again.")
    return text


def generate_structured(
    prompt: str, *, temperature: float = DEFAULT_TEMPERATURE
) -> StructuredAIResponse:
    """Send a prompt expecting a JSON object with 'summary' and 'key_takeaways'."""
    client = _build_client()
    config = get_config()

    try:
        response = client.models.generate_content(
            model=config.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json",
            ),
        )
    except genai_errors.APIError as exc:
        logger.warning("Gemini API error: %s", exc)
        raise _classify_error(exc) from exc
    except Exception as exc:
        logger.warning("Unexpected error calling Gemini: %s", exc)
        raise _classify_error(exc) from exc

    raw_text = _extract_text(response)
    if not raw_text:
        raise AIEmptyResponseError("Gemini returned an empty response. Please try again.")

    parsed = _safe_parse_json(raw_text)
    summary = str(parsed.get("summary", "")).strip()
    takeaways = parsed.get("key_takeaways", []) or []
    takeaways = [str(t).strip() for t in takeaways if str(t).strip()]

    if not summary:
        raise AIEmptyResponseError("Gemini returned an empty summary. Please try again.")

    return StructuredAIResponse(summary=summary, key_takeaways=takeaways)


def _safe_parse_json(raw_text: str) -> dict:
    """Parse JSON from the model's response, tolerating stray markdown code fences."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Failed to parse Gemini JSON response; falling back to raw text.")
        return {"summary": raw_text, "key_takeaways": []}
