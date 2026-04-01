"""
rag_pipeline.py
───────────────
Top-level orchestrator that wires all modules into a single coherent pipeline.

Pipeline (per query):
  Query
    → Retriever     (FAISS vector search, top-k candidates)
    → Reranker      (cross-encoder, top-k reranked)
    → ContextBuilder (format references for prompt)
    → GeminiClient  (generate grounded answer with citations)
    → MemoryManager (store turn, provide history for next turn)
    → RAGResponse   (returned to frontend)
"""

from dataclasses import dataclass, field
from typing import List, Optional

from backend.config import settings
from backend.context_builder import ContextBuilder, LegalReference
from backend.embedding_model import EmbeddingModel
from backend.llm_client import CohereClient
from backend.memory_manager import MemoryManager
from backend.reranker import Reranker
from backend.retriever import Retriever
from backend.vector_store import VectorStore
from utils.logger import logger


# ─── Response object ─────────────────────────────────────────────────────────

@dataclass
class RAGResponse:
    """Structured response returned to the caller / frontend."""
    query: str
    answer: str
    references: List[LegalReference] = field(default_factory=list)
    num_candidates_retrieved: int = 0
    num_references_used: int = 0
    error: Optional[str] = None


# ─── Pipeline ────────────────────────────────────────────────────────────────

class RAGPipeline:
    """
    Full Retrieval-Augmented Generation pipeline for legal queries.

    Usage:
        pipeline = RAGPipeline()
        response = pipeline.query("What is the punishment for theft under BNS?")
        print(response.answer)
        for ref in response.references:
            print(ref.act_name, ref.section_number)
    """

    def __init__(self) -> None:
        logger.info("Initialising RAG Pipeline …")

        # Load models (expensive – done once at startup)
        self.embedding_model = EmbeddingModel()
        self.reranker = Reranker()
        self.llm = CohereClient()

        # Load Weaviate vector store
        self.vector_store = VectorStore()
        self.vector_store.connect()
        self.vector_store.load()

        # Instantiate pipeline components
        self.retriever = Retriever(
            vector_store=self.vector_store,
            embedding_model=self.embedding_model,
            top_k=settings.top_k_retrieval,
        )
        self.context_builder = ContextBuilder()

        # Conversation memory (per pipeline instance = per session)
        self.memory = MemoryManager()

        logger.info(
            f"RAG Pipeline ready | "
            f"index_size={self.vector_store.total_vectors} vectors"
        )

    # ── Main query entry point ────────────────────────────────────────────

    def query(self, user_query: str, external_history: List[dict] | None = None) -> RAGResponse:
        """Non-streaming query — returns complete RAGResponse."""
        logger.info(f"Processing query: '{user_query[:100]}'")
        try:
            candidates  = self.retriever.retrieve(user_query)
            reranked    = self.reranker.rerank(user_query, candidates, top_k=settings.top_k_reranked)
            context_str, references = self.context_builder.build(reranked)
            history     = external_history if external_history is not None else self.memory.get_history()
            answer      = self.llm.generate(context=context_str, query=user_query, history=history)
            self.memory.add_turn(user_query, answer)
            return RAGResponse(
                query=user_query, answer=answer, references=references,
                num_candidates_retrieved=len(candidates),
                num_references_used=len(references),
            )
        except Exception as exc:
            logger.error(f"Pipeline error: {exc}")
            return RAGResponse(
                query=user_query,
                answer="I encountered an error processing your query. Please try again.",
                error=str(exc),
            )

    def stream_query(
        self,
        user_query: str,
        external_history: List[dict] | None = None,
    ):
        """
        Streaming query — yields dicts as the answer is generated.

        Yields:
            {"type": "references", "data": [LegalReference, ...]}
            {"type": "chunk",      "text": "...partial text..."}
            {"type": "done",       "full_answer": "...complete answer..."}
            {"type": "error",      "message": "...error message..."}
        """
        logger.info(f"Streaming query: '{user_query[:100]}'")
        try:
            candidates  = self.retriever.retrieve(user_query)
            reranked    = self.reranker.rerank(user_query, candidates, top_k=settings.top_k_reranked)
            context_str, references = self.context_builder.build(reranked)
            history     = external_history if external_history is not None else self.memory.get_history()

            # Emit references immediately so sidebar updates before text starts
            yield {"type": "references", "data": references}

            # Stream LLM tokens
            full_answer = ""
            for chunk_text in self.llm.generate_stream(
                context=context_str, query=user_query, history=history
            ):
                full_answer += chunk_text
                yield {"type": "chunk", "text": chunk_text}

            self.memory.add_turn(user_query, full_answer)
            yield {"type": "done", "full_answer": full_answer}

        except Exception as exc:
            logger.error(f"Stream pipeline error: {exc}")
            yield {"type": "error", "message": str(exc)}

    def reset_memory(self) -> None:
        """Clear conversation memory to start a fresh session."""
        self.memory.clear()
        logger.info("Pipeline memory reset")