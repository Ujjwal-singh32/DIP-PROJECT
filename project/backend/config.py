"""
config.py
─────────
Centralised settings loaded from environment variables via Pydantic-Settings.

.env file is searched in this order:
  1. Current working directory       (project/.env)
  2. Parent of current directory     (DIP project/.env)
  3. Script file's parent directory  (project/.env)
  4. Two levels up                   (Desktop/.env)

So wherever your .env is, it will be found automatically.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> Path:
    """
    Search common locations for the .env file and return the first one found.
    Falls back to '.env' (current dir) if none found — pydantic will just
    rely on actual environment variables in that case.
    """
    search_paths = [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        Path(__file__).parent.parent / ".env",
        Path(__file__).parent.parent.parent / ".env",
    ]

    for path in search_paths:
        if path.exists():
            print(f"[config] Found .env at: {path}")
            return path

    print("[config] WARNING: .env file not found in any standard location.")
    print("[config] Searched:")
    for p in search_paths:
        print(f"           {p}")

    print("[config] Falling back to OS environment variables.")
    return Path(".env")


_ENV_FILE = _find_env_file()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Gemini ──────────────────────────────────────────────────────
    gemini_api_key: str = Field(
        ..., validation_alias="GEMINI_API_KEY", description="Google Gemini API key"
    )

    gemini_model: str = Field(
        "gemini-1.5-flash",
        validation_alias="GEMINI_MODEL",
        description="Gemini model name",
    )

    # ── MongoDB ─────────────────────────────────────────────────────
    mongodb_uri: str = Field(
        "mongodb://localhost:27017",
        validation_alias="MONGODB_URI",
        description="MongoDB URI",
    )

    mongo_db_name: str = Field(
        "legal_rag",
        validation_alias="MONGO_DB_NAME",
        description="MongoDB database name",
    )

    mongo_collection: str = Field(
        "law_sections",
        validation_alias="MONGO_COLLECTION",
        description="MongoDB collection",
    )

    # ── Embedding ───────────────────────────────────────────────────
    embedding_model: str = Field(
        "intfloat/e5-large",
        validation_alias="EMBEDDING_MODEL",
        description="HuggingFace embedding model",
    )

    # ── Reranker ────────────────────────────────────────────────────
    reranker_model: str = Field(
        "cross-encoder/ms-marco-MiniLM-L-6-v2",
        validation_alias="RERANKER_MODEL",
        description="Cross-encoder reranker model",
    )

    # ── FAISS ───────────────────────────────────────────────────────
    faiss_index_path: Path = Field(
        Path("./data/faiss_index"),
        description="FAISS binary index file path",
    )

    faiss_metadata_path: Path = Field(
        Path("./data/faiss_metadata.json"),
        description="FAISS metadata JSON file path",
    )

    # ── Retrieval ───────────────────────────────────────────────────
    top_k_retrieval: int = Field(10, description="Number of docs to retrieve")
    top_k_reranked: int = Field(4, description="Number of docs after reranking")

    # ── Chunking ────────────────────────────────────────────────────
    chunk_size: int = Field(512, description="Token chunk size")
    chunk_overlap: int = Field(64, description="Token overlap between chunks")

    # ── Memory ──────────────────────────────────────────────────────
    memory_type: Literal["buffer", "summary"] = Field(
        "buffer", description="LangChain memory type"
    )

    max_history_tokens: int = Field(
        2000, description="Max token budget for history"
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings singleton."""
    return Settings()


settings = get_settings()