"""
embedding_model.py
──────────────────
Wraps SentenceTransformers to produce dense vector embeddings.

Supports:
  • intfloat/e5-large  (default – best retrieval quality)
  • law-ai/InLegalBERT (domain-specialised Indian legal BERT)

E5 models require queries to be prefixed with "query: " and documents
with "passage: " for optimal retrieval performance.
"""

from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from backend.config import settings
from utils.logger import logger


class EmbeddingModel:
    """
    Thin wrapper around SentenceTransformer.

    Usage:
        model = EmbeddingModel()
        doc_vecs  = model.embed_documents(["text1", "text2"])
        query_vec = model.embed_query("What is theft punishment?")
    """

    # Models that need the e5-style prefix treatment
    _E5_PREFIX_MODELS = {"intfloat/e5-large", "intfloat/e5-base", "intfloat/e5-small"}

    def __init__(self, model_name: str = settings.embedding_model) -> None:
        self.model_name = model_name
        self._use_e5_prefix = model_name in self._E5_PREFIX_MODELS

        logger.info(f"Loading embedding model: {model_name}")
        self._model = SentenceTransformer(model_name)
        self.dimension = self._model.get_sentence_embedding_dimension()
        logger.info(
            f"Embedding model loaded | dimension={self.dimension} "
            f"| e5_prefix={self._use_e5_prefix}"
        )

    # ── Internal helpers ──────────────────────────────────────────────────

    def _prefix_docs(self, texts: List[str]) -> List[str]:
        if self._use_e5_prefix:
            return [f"passage: {t}" for t in texts]
        return texts

    def _prefix_query(self, query: str) -> str:
        if self._use_e5_prefix:
            return f"query: {query}"
        return query

    # ── Public API ────────────────────────────────────────────────────────

    def embed_documents(
        self,
        texts: List[str],
        batch_size: int = 64,
        show_progress: bool = True,
    ) -> np.ndarray:
        """
        Embed a list of document texts.

        Returns:
            np.ndarray of shape (len(texts), dimension), dtype float32.
        """
        prefixed = self._prefix_docs(texts)
        logger.info(f"Embedding {len(prefixed)} documents …")
        vectors = self._model.encode(
            prefixed,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,   # cosine similarity via inner product
            convert_to_numpy=True,
        )
        logger.info(f"Embeddings generated | shape={vectors.shape}")
        return vectors.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query string.

        Returns:
            np.ndarray of shape (dimension,), dtype float32.
        """
        prefixed = self._prefix_query(query)
        vector = self._model.encode(
            prefixed,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return vector.astype(np.float32)