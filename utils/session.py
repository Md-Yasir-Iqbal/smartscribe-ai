"""
Session-state management for SmartScribe AI.

No database is used in this version — all state lives in Streamlit's
``session_state`` for the duration of the browser session. The data model is
intentionally kept simple (a small dataclass) so a real database could be
introduced later without changing any UI component's public interface.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

import streamlit as st

from utils.helpers import generate_short_title, timestamp_now
from utils.metrics import count_words


@dataclass
class HistoryEntry:
    id: str
    timestamp: datetime
    input_type: str  # "Text" or "PDF"
    title: str
    summary: str
    key_takeaways: List[str]
    mode: str
    original_text: str
    summary_word_count: int
    original_word_count: int
    settings: Dict[str, str] = field(default_factory=dict)


_DEFAULTS = {
    "page": "Home",
    "history": [],
    "active_result_id": None,
    "text_input_value": "",
}


def init_session_state() -> None:
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_page(page: str) -> None:
    st.session_state["page"] = page


def get_page() -> str:
    return st.session_state.get("page", "Home")


def add_history_entry(
    *,
    input_type: str,
    summary: str,
    key_takeaways: List[str],
    mode: str,
    original_text: str,
    source_title: Optional[str] = None,
    settings: Dict[str, str],
) -> HistoryEntry:
    entry = HistoryEntry(
        id=str(uuid.uuid4()),
        timestamp=timestamp_now(),
        input_type=input_type,
        title=source_title or generate_short_title(original_text),
        summary=summary,
        key_takeaways=key_takeaways,
        mode=mode,
        original_text=original_text,
        summary_word_count=count_words(summary),
        original_word_count=count_words(original_text),
        settings=settings,
    )
    st.session_state.setdefault("history", [])
    st.session_state["history"].insert(0, entry)
    st.session_state["active_result_id"] = entry.id
    return entry


def get_history() -> List[HistoryEntry]:
    return st.session_state.get("history", [])


def get_history_entry(entry_id: str) -> Optional[HistoryEntry]:
    for entry in get_history():
        if entry.id == entry_id:
            return entry
    return None


def clear_history() -> None:
    st.session_state["history"] = []
    st.session_state["active_result_id"] = None


def set_active_result(entry_id: Optional[str]) -> None:
    st.session_state["active_result_id"] = entry_id


def get_active_result() -> Optional[HistoryEntry]:
    entry_id = st.session_state.get("active_result_id")
    if not entry_id:
        return None
    return get_history_entry(entry_id)
