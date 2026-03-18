"""
scripts/build_vector_index.py
──────────────────────────────
Builds the Weaviate vector index from MongoDB law sections.

EMBEDDING CACHE:
  Embeddings are saved to ./data/embeddings_cache.npz after Step 3.
  If the cache exists, Step 3 is skipped entirely — saving 8+ minutes.
  Use --force-embed to ignore cache and regenerate.

Usage:
    python scripts/build_vector_index.py                  # uses cache if exists
    python scripts/build_vector_index.py --force-embed    # regenerate embeddings
    python scripts/build_vector_index.py --domain criminal_law
"""

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings
from backend.embedding_model import EmbeddingModel
from backend.mongo_loader import load_law_sections
from backend.text_processor import TextChunk, TextProcessor
from backend.vector_store import VectorStore
from utils.helpers import ensure_dir, save_json, load_json
from utils.logger import logger

# ── Cache file paths ──────────────────────────────────────────────────────────
CACHE_DIR        = Path("./data")
EMBEDDINGS_CACHE = CACHE_DIR / "embeddings_cache.npz"
CHUNKS_CACHE     = CACHE_DIR / "chunks_cache.json"


def save_cache(chunks: list[TextChunk], embeddings: np.ndarray) -> None:
    """Save embeddings and chunks to disk so we never recompute them."""
    ensure_dir(CACHE_DIR)

    # Save embeddings as compressed numpy file
    np.savez_compressed(str(EMBEDDINGS_CACHE), embeddings=embeddings)
    logger.info(f"Embeddings cached → {EMBEDDINGS_CACHE}")

    # Save chunk metadata as JSON
    chunks_data = [
        {
            "text":           c.text,
            "act_name":       c.act_name,
            "act_year":       c.act_year,
            "section_number": c.section_number,
            "section_title":  c.section_title,
            "domain":         c.domain,
            "clause_text":    c.clause_text,
            "source_pdf":     c.source_pdf,
            "source_url":     c.source_url,
            "chunk_index":    c.chunk_index,
            "total_chunks":   c.total_chunks,
        }
        for c in chunks
    ]
    save_json(chunks_data, CHUNKS_CACHE)
    logger.info(f"Chunks cached     → {CHUNKS_CACHE}")


def load_cache() -> tuple[list[TextChunk], np.ndarray]:
    """Load embeddings and chunks from disk cache."""
    logger.info("Loading embeddings from cache …")

    # Load embeddings
    data = np.load(str(EMBEDDINGS_CACHE))
    embeddings = data["embeddings"]
    logger.info(f"Embeddings loaded from cache | shape={embeddings.shape}")

    # Load chunks
    chunks_data = load_json(CHUNKS_CACHE)
    chunks = [
        TextChunk(
            text=           c["text"],
            act_name=       c["act_name"],
            act_year=       c["act_year"],
            section_number= c["section_number"],
            section_title=  c["section_title"],
            domain=         c["domain"],
            clause_text=    c["clause_text"],
            source_pdf=     c["source_pdf"],
            source_url=     c["source_url"],
            chunk_index=    c["chunk_index"],
            total_chunks=   c["total_chunks"],
        )
        for c in chunks_data
    ]
    logger.info(f"Chunks loaded from cache | count={len(chunks)}")

    return chunks, embeddings


def cache_exists() -> bool:
    return EMBEDDINGS_CACHE.exists() and CHUNKS_CACHE.exists()


# ── Main build function ───────────────────────────────────────────────────────

def build_index(domain: str | None = None, force_embed: bool = False) -> None:

    # ── 1. Load from MongoDB ──────────────────────────────────────────────
    logger.info("Step 1/4 — Loading law sections from MongoDB …")
    sections = load_law_sections(domain=domain)

    if not sections:
        logger.error(
            "No sections found in MongoDB. "
            "Run `python scripts/load_mongo_data.py` first."
        )
        sys.exit(1)
    logger.info(f"Loaded {len(sections)} law sections")

    # ── 2. Text processing ────────────────────────────────────────────────
    logger.info("Step 2/4 — Chunking sections …")
    processor = TextProcessor()
    chunks: list[TextChunk] = processor.process_all(sections)
    logger.info(f"Created {len(chunks)} text chunks")

    # ── 3. Generate OR load embeddings ────────────────────────────────────
    if not force_embed and cache_exists():
        logger.info(
            "Step 3/4 — ✅ Embedding cache found! Skipping embedding generation.\n"
            "           (Run with --force-embed to regenerate)"
        )
        cached_chunks, embeddings = load_cache()

        # Validate cache matches current chunks
        if len(cached_chunks) != len(chunks):
            logger.warning(
                f"Cache has {len(cached_chunks)} chunks but MongoDB has {len(chunks)}.\n"
                "Regenerating embeddings …"
            )
            force_embed = True
        else:
            chunks = cached_chunks   # use cached chunks (already processed)

    if force_embed or not cache_exists():
        logger.info("Step 3/4 — Generating embeddings … (this takes 5-10 mins)")
        embedding_model = EmbeddingModel()
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_model.embed_documents(
            texts, batch_size=32, show_progress=True
        )
        # Save to cache immediately so crash won't lose work
        save_cache(chunks, embeddings)
        logger.info("Embeddings saved to cache ✅")
    else:
        # Get dimension from cached embeddings
        embedding_model = EmbeddingModel.__new__(EmbeddingModel)
        embedding_model.dimension = embeddings.shape[1]
        embedding_model.model_name = settings.embedding_model
        logger.info(f"Using cached embeddings | dimension={embeddings.shape[1]}")

    # ── 4. Insert into FAISS ─────────────────────────────────────────────
    logger.info("Step 4/4 — Building FAISS index …")
    store = VectorStore()
    store.connect()
    store.create_collection(
        dimension=embeddings.shape[1],
        recreate=True,
    )
    store.add(chunks, embeddings)
    store.disconnect()

    logger.info(
        f"\n{'─'*50}\n"
        f"✅  FAISS index built successfully!\n"
        f"    Vectors   : {store.total_vectors}\n"
        f"    Dimension : {embeddings.shape[1]}\n"
        f"    Index     : ./data/faiss_index\n"
        f"    Metadata  : ./data/faiss_metadata.json\n"
        f"{'─'*50}\n"
        f"Next step → streamlit run frontend/streamlit_app.py"
    )


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the Weaviate vector index from MongoDB law sections"
    )
    parser.add_argument(
        "--domain",
        type=str,
        default=None,
        help="Filter by domain (e.g. criminal_law). Default: all domains.",
    )
    parser.add_argument(
        "--force-embed",
        action="store_true",
        help="Ignore embedding cache and regenerate from scratch.",
    )
    args = parser.parse_args()
    build_index(domain=args.domain, force_embed=args.force_embed)


if __name__ == "__main__":
    main()