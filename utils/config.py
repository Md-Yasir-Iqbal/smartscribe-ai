"""
Central configuration module for SmartScribe AI.

Configuration values are resolved in this order of precedence:
1. Streamlit Secrets (``st.secrets``) — used automatically on Streamlit
   Community Cloud once secrets are set in the app dashboard.
2. Environment variables — used for local development, typically loaded
   from a ``.env`` file via python-dotenv.

No API keys or secrets are ever hard-coded in this file or anywhere else
in the codebase.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

try:
    from dotenv import load_dotenv

    load_dotenv()  # no-op if no .env file exists — safe on Streamlit Cloud
except ImportError:  # pragma: no cover - dotenv is a declared dependency
    pass

import streamlit as st

# --------------------------------------------------------------------------
# Defaults and limits (safe, non-secret values only)
# --------------------------------------------------------------------------

# Current, actively supported Gemini model. This is only a *default* — it
# can be overridden at any time via the GEMINI_MODEL environment variable
# or Streamlit secret, without touching any application code.
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"

# Pasted-text limits (characters)
MIN_TEXT_CHARS = 40
MAX_TEXT_CHARS = 100_000

# Chunking configuration for long documents
CHUNK_THRESHOLD_CHARS = 7_000   # only chunk if cleaned text exceeds this
CHUNK_SIZE_CHARS = 6_000
CHUNK_OVERLAP_CHARS = 300

# PDF upload limits
MAX_PDF_SIZE_MB = 20
MAX_PDF_PAGES = 300

# Reading-time estimate
READING_WPM = 200


def _get_secret(key: str) -> Optional[str]:
    """
    Look up a single configuration value, preferring Streamlit Secrets
    (Streamlit Community Cloud) and falling back to environment variables
    (local development).
    """
    try:
        # st.secrets raises if no secrets.toml exists at all, which is the
        # normal situation for local development without Streamlit secrets.
        if key in st.secrets:
            value = st.secrets[key]
            if value:
                return str(value)
    except Exception:
        pass

    value = os.environ.get(key)
    return value if value else None


@dataclass(frozen=True)
class AppConfig:
    gemini_api_key: Optional[str]
    gemini_model: str

    @property
    def is_configured(self) -> bool:
        return bool(self.gemini_api_key)


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Return the resolved application configuration (cached per process)."""
    api_key = _get_secret("GEMINI_API_KEY")
    model = _get_secret("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL
    return AppConfig(gemini_api_key=api_key, gemini_model=model)
