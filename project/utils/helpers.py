"""
helpers.py
──────────
Miscellaneous utility functions shared across the project.
"""

import json
import time
from pathlib import Path
from typing import Any

from utils.logger import logger


def ensure_dir(path: Path) -> Path:
    """Create directory (and parents) if it doesn't exist."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(data: Any, path: Path) -> None:
    """Serialise data to a JSON file."""
    path = Path(path)
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    logger.debug(f"Saved JSON → {path}")


def load_json(path: Path) -> Any:
    """Load data from a JSON file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def timeit(func):
    """Decorator that logs function execution time."""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.debug(f"{func.__qualname__} completed in {elapsed:.3f}s")
        return result
    return wrapper


def truncate_text(text: str, max_chars: int = 300) -> str:
    """Return a truncated version of text for display purposes."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"


def clean_text(text: str) -> str:
    """Basic text normalisation: strip excess whitespace."""
    import re
    text = re.sub(r"\s+", " ", text)
    return text.strip()