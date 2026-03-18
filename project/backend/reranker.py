"""
reranker.py
───────────
Cross-encoder reranker that re-scores FAISS candidates based on
query–document relevance.

Why rerank?
  Bi-encoder embeddings (used in FAISS) are fast but approximate.
  A cross-encoder sees (query, document) jointly and produces a much more
  accurate relevance score at the cost of higher latency.

Model: cross-encoder/ms-marco-MiniLM-L-6-v2
"""

from typing import List, Tuple

from sentence_transformers import CrossEncoder

from backend.config import settings
from utils.logger import logger


class Reranker:
    """
    Cross-encoder reranker.

    Usage:
        reranker = Reranker()
        top_docs = reranker.rerank(query, candidates, top_k=4)
    """

    def __init__(self, model_name: str = settings.reranker_model) -> None:
        logger.info(f"Loading reranker model: {model_name}")
        self._model = CrossEncoder(model_name, max_length=512)
        logger.info("Reranker model loaded")

    def rerank(
        self,
        query: str,
        candidates: List[Tuple[dict, float]],
        top_k: int = settings.top_k_reranked,
    ) -> List[Tuple[dict, float]]:
        """
        Re-score and rank candidate documents.

        Args:
            query:      The user's query string.
            candidates: List of (metadata_dict, faiss_score) from the retriever.
            top_k:      Number of top results to return after reranking.

        Returns:
            Sorted list of (metadata_dict, reranker_score), highest first.
        """
        if not candidates:
            return []

        # Build (query, document_text) pairs for the cross-encoder
        pairs = [(query, meta["text"]) for meta, _ in candidates]

        logger.info(f"Reranking {len(pairs)} candidates …")
        scores = self._model.predict(pairs)

        # Attach reranker scores and sort descending
        scored = [
            (meta, float(score))
            for (meta, _), score in zip(candidates, scores)
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        top = scored[:top_k]
        logger.info(
            f"Reranking complete | top-{top_k} scores: "
            f"{[round(s, 3) for _, s in top]}"
        )
        return top