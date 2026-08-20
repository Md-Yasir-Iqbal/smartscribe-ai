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
import time
from dataclasses import dataclass
from typing import Callable, List, TypeVar

import streamlit as st
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from utils.config import get_config

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_MS = 60_000
DEFAULT_TEMPERATURE = 0.3

# Transient errors (server-side hiccups, timeouts, brief rate limiting) are
# retried automatically with a short backoff before being surfaced to the
# user. Quota and invalid-key errors are never retried — retrying can't fix
# either of those.
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 1.5

_T = TypeVar("_T")


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


class AIServerError(AIServiceError):
    """Gemini returned a 5xx server error. This is transient and safe to retry."""


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
                return AIServerError(
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


# Errors worth retrying automatically: a brief server hiccup, a timeout, or a
# short burst of rate limiting are all commonly transient. Quota errors and
# invalid-key errors are deliberately excluded — retrying won't fix either.
_RETRYABLE_ERROR_TYPES = (AIServerError, AITimeoutError, AIRateLimitError)


def _call_gemini_with_retry(make_call: Callable[[], _T]) -> _T:
    """Call Gemini, retrying up to MAX_RETRIES times (with a short backoff)
    if the failure looks transient. Chunked/long documents make several
    sequential Gemini calls, so a single blip shouldn't fail the whole run."""
    last_error: AIServiceError = AIServiceError("Gemini request failed.")

    for attempt in range(MAX_RETRIES + 1):
        try:
            return make_call()
        except genai_errors.APIError as exc:
            last_error = _classify_error(exc)
        except Exception as exc:  # network errors, timeouts, etc.
            last_error = _classify_error(exc)

        is_last_attempt = attempt == MAX_RETRIES
        if not isinstance(last_error, _RETRYABLE_ERROR_TYPES) or is_last_attempt:
            logger.warning("Gemini call failed (attempt %s): %s", attempt + 1, last_error)
            raise last_error from None

        logger.warning(
            "Transient Gemini error on attempt %s/%s, retrying: %s",
            attempt + 1, MAX_RETRIES + 1, last_error,
        )
        time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))

    raise last_error  # pragma: no cover — loop always returns or raises above


def generate_text(prompt: str, *, temperature: float = DEFAULT_TEMPERATURE) -> str:
    """Send a plain-text prompt to Gemini and return the plain-text response."""
    client = _build_client()
    config = get_config()

    def make_call():
        return client.models.generate_content(
            model=config.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=temperature),
        )

    response = _call_gemini_with_retry(make_call)

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

    def make_call():
        return client.models.generate_content(
            model=config.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json",
            ),
        )

    response = _call_gemini_with_retry(make_call)

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
