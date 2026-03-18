"""
retriever.py
────────────
Performs semantic retrieval from the FAISS vector store.

Responsibilities:
  1. Embed the incoming query.
  2. Search the FAISS index.
  3. Return raw candidate results to the reranker.
"""

from typing import List, Tuple

from backend.config import settings
from backend.embedding_model import EmbeddingModel
from backend.vector_store import VectorStore
from utils.logger import logger


class Retriever:
    """
    Semantic retriever backed by FAISS.

    Usage:
        retriever = Retriever()
        candidates = retriever.retrieve("What is the punishment for theft?")
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_model: EmbeddingModel,
        top_k: int = settings.top_k_retrieval,
    ) -> None:
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.top_k = top_k

    def retrieve(self, query: str) -> List[Tuple[dict, float]]:
        """
        Retrieve top-k candidate law sections for `query`.

        Args:
            query: Natural language legal question.

        Returns:
            List of (metadata_dict, similarity_score) tuples.
        """
        logger.info(f"Retrieving top-{self.top_k} candidates for: '{query[:80]}…'")
        query_vector = self.embedding_model.embed_query(query)
        results = self.vector_store.search(query_vector, top_k=self.top_k)
        logger.info(f"Retrieved {len(results)} candidates from FAISS")
        return results