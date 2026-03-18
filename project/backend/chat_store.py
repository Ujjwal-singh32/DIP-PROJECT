"""
backend/chat_store.py
─────────────────────
Persistent chat session storage using JSON files on disk.

Each chat session is stored as a separate JSON file:
    data/chats/<chat_id>.json

Structure of each chat file:
{
    "chat_id": "abc12345",
    "title": "What is theft under BNS?",
    "created_at": "2026-03-16T12:00:00",
    "updated_at": "2026-03-16T12:05:00",
    "messages": [
        {
            "role": "user" | "assistant",
            "content": "...",
            "references": [...],   # only for assistant messages
            "timestamp": "..."
        }
    ]
}
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from utils.logger import logger

# ── Storage directory ─────────────────────────────────────────────────────────
CHATS_DIR = Path("./data/chats")


def _ensure_chats_dir():
    CHATS_DIR.mkdir(parents=True, exist_ok=True)


def _chat_path(chat_id: str) -> Path:
    return CHATS_DIR / f"{chat_id}.json"


def _now() -> str:
    return datetime.now().isoformat()


# ── Core CRUD ─────────────────────────────────────────────────────────────────

def create_chat(first_message: str = "") -> dict:
    """
    Create a new chat session and save it to disk.

    Args:
        first_message: Used to generate the chat title.

    Returns:
        The new chat dict.
    """
    _ensure_chats_dir()
    chat_id = str(uuid.uuid4())[:8]   # short 8-char ID like GPT

    # Auto-title from first message (truncated)
    title = first_message[:50].strip() if first_message else "New Chat"
    if len(first_message) > 50:
        title += "…"

    chat = {
        "chat_id":    chat_id,
        "title":      title,
        "created_at": _now(),
        "updated_at": _now(),
        "messages":   [],
    }
    _save_chat(chat)
    logger.info(f"Created chat | id={chat_id} | title='{title}'")
    return chat


def load_chat(chat_id: str) -> Optional[dict]:
    """Load a chat session from disk. Returns None if not found."""
    path = _chat_path(chat_id)
    if not path.exists():
        logger.warning(f"Chat not found: {chat_id}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_chat(chat: dict) -> None:
    """Save a chat session to disk."""
    _ensure_chats_dir()
    chat["updated_at"] = _now()
    path = _chat_path(chat["chat_id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chat, f, ensure_ascii=False, indent=2)


def add_message(chat_id: str, role: str, content: str, references: list = None) -> dict:
    """
    Append a message to an existing chat and persist it.

    Args:
        chat_id:    The chat session ID.
        role:       'user' or 'assistant'.
        content:    Message text.
        references: List of LegalReference dicts (assistant only).

    Returns:
        The updated chat dict.
    """
    chat = load_chat(chat_id)
    if not chat:
        raise ValueError(f"Chat {chat_id} not found")

    # Serialise LegalReference dataclasses to plain dicts
    serialised_refs = []
    if references:
        for ref in references:
            if hasattr(ref, "__dict__"):
                serialised_refs.append(ref.__dict__)
            elif isinstance(ref, dict):
                serialised_refs.append(ref)

    message = {
        "role":       role,
        "content":    content,
        "references": serialised_refs,
        "timestamp":  _now(),
    }
    chat["messages"].append(message)

    # Update title from first user message if still default
    if role == "user" and chat["title"] == "New Chat":
        chat["title"] = content[:50].strip() + ("…" if len(content) > 50 else "")

    _save_chat(chat)
    return chat


def list_chats() -> List[dict]:
    """
    Return all chats sorted by updated_at descending (most recent first).
    Returns summary dicts (no messages) for sidebar display.
    """
    _ensure_chats_dir()
    chats = []
    for path in CHATS_DIR.glob("*.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                chat = json.load(f)
            # Return summary only (skip messages for performance)
            chats.append({
                "chat_id":    chat["chat_id"],
                "title":      chat.get("title", "Untitled"),
                "created_at": chat.get("created_at", ""),
                "updated_at": chat.get("updated_at", ""),
                "message_count": len(chat.get("messages", [])),
            })
        except Exception as e:
            logger.warning(f"Could not load chat file {path}: {e}")

    chats.sort(key=lambda x: x["updated_at"], reverse=True)
    return chats


def delete_chat(chat_id: str) -> bool:
    """Delete a chat session from disk. Returns True if deleted."""
    path = _chat_path(chat_id)
    if path.exists():
        path.unlink()
        logger.info(f"Deleted chat: {chat_id}")
        return True
    return False


def rename_chat(chat_id: str, new_title: str) -> bool:
    """Rename a chat session."""
    chat = load_chat(chat_id)
    if not chat:
        return False
    chat["title"] = new_title[:60]
    _save_chat(chat)
    return True


def get_chat_history_for_llm(chat_id: str) -> List[dict]:
    """
    Return chat messages formatted for the LLM memory manager.
    Format: [{"role": "user"|"assistant", "content": "..."}]
    """
    chat = load_chat(chat_id)
    if not chat:
        return []
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in chat.get("messages", [])
    ]