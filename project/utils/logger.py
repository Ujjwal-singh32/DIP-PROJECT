"""
logger.py
─────────
Centralised Loguru logger configuration.
Import `logger` from this module everywhere in the project.
"""

import sys
from loguru import logger

# Remove the default handler
logger.remove()

# Console handler – human-readable, colourised
logger.add(
    sys.stderr,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    level="INFO",
    colorize=True,
)

# File handler – JSON-structured for production log aggregation
logger.add(
    "logs/legal_rag.log",
    rotation="10 MB",
    retention="7 days",
    compression="gz",
    format="{time} | {level} | {name}:{function}:{line} | {message}",
    level="DEBUG",
    enqueue=True,          # thread-safe async write
)

__all__ = ["logger"]