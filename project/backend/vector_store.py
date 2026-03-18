# """
# vector_store.py  (Weaviate backend)
# ────────────────────────────────────
# Replaces FAISS with Weaviate as the vector database.

# Weaviate stores BOTH the vectors AND the metadata together in one place
# (unlike FAISS which needs a separate JSON metadata file).

# Setup:
#     pip install weaviate-client

# Run Weaviate locally via Docker:
#     docker run -d \
#       -p 8080:8080 -p 50051:50051 \
#       --name weaviate \
#       cr.weaviate.io/semitechnologies/weaviate:latest

# Or use Weaviate Cloud (free tier): https://console.weaviate.cloud
# """

# from dataclasses import asdict
# from typing import List, Tuple

# import weaviate
# import weaviate.classes as wvc
# from weaviate.classes.config import Configure, Property, DataType
# from weaviate.classes.query import MetadataQuery

# from backend.config import settings
# from backend.text_processor import TextChunk
# from utils.logger import logger


# # Name of the Weaviate collection (like a table name)
# COLLECTION_NAME = "LawSection"


# class VectorStore:
#     """
#     Weaviate-backed vector store.

#     Weaviate stores vectors + metadata together in one place.
#     No separate JSON file needed (unlike FAISS).

#     Usage (indexing):
#         store = VectorStore()
#         store.connect()
#         store.create_collection(dimension=1024)
#         store.add(chunks, embeddings)
#         store.disconnect()

#     Usage (retrieval):
#         store = VectorStore()
#         store.connect()
#         store.load()
#         results = store.search(query_vector, top_k=10)
#         store.disconnect()
#     """

#     def __init__(self) -> None:
#         self._client: weaviate.WeaviateClient | None = None
#         self._collection = None
#         self._total: int = 0

#     # ── Connection ────────────────────────────────────────────────────────

#     def connect(self) -> None:
#         """Connect to Weaviate (local Docker or Weaviate Cloud)."""
#         weaviate_url = getattr(settings, "weaviate_url", "http://localhost:8080")
#         weaviate_api_key = getattr(settings, "weaviate_api_key", None)

#         logger.info(f"Connecting to Weaviate at {weaviate_url} …")

#         if "localhost" in weaviate_url or "127.0.0.1" in weaviate_url:
#             # Local Docker connection
#             self._client = weaviate.connect_to_local(
#                 host="localhost",
#                 port=8080,
#                 grpc_port=50051,
#             )
#         else:
#             # Weaviate Cloud connection
#             self._client = weaviate.connect_to_weaviate_cloud(
#                 cluster_url=weaviate_url,
#                 auth_credentials=weaviate.auth.AuthApiKey(weaviate_api_key),
#             )

#         logger.info("Weaviate connected ✅")

#     def disconnect(self) -> None:
#         """Close the Weaviate connection."""
#         if self._client:
#             self._client.close()
#             logger.info("Weaviate disconnected")

#     # ── Collection management ─────────────────────────────────────────────

#     def create_collection(self, dimension: int, recreate: bool = False) -> None:
#         """
#         Create the LawSection collection in Weaviate.

#         Args:
#             dimension: Embedding vector dimension (1024 for e5-large).
#             recreate:  Drop and recreate if True.
#         """
#         if recreate and self._client.collections.exists(COLLECTION_NAME):
#             self._client.collections.delete(COLLECTION_NAME)
#             logger.warning(f"Dropped existing collection '{COLLECTION_NAME}'")

#         if self._client.collections.exists(COLLECTION_NAME):
#             logger.info(f"Collection '{COLLECTION_NAME}' already exists — skipping")
#             self._collection = self._client.collections.get(COLLECTION_NAME)
#             return

#         logger.info(
#             f"Creating Weaviate collection '{COLLECTION_NAME}' "
#             f"| dimension={dimension} …"
#         )

#         self._collection = self._client.collections.create(
#             name=COLLECTION_NAME,

#             # We bring our own vectors — no Weaviate-side vectorizer
#             vectorizer_config=Configure.Vectorizer.none(),

#             # Schema: one property per metadata field
#             properties=[
#                 Property(name="text",           data_type=DataType.TEXT),
#                 Property(name="act_name",        data_type=DataType.TEXT),
#                 Property(name="act_year",        data_type=DataType.INT),
#                 Property(name="section_number",  data_type=DataType.TEXT),
#                 Property(name="section_title",   data_type=DataType.TEXT),
#                 Property(name="domain",          data_type=DataType.TEXT),
#                 Property(name="clause_text",     data_type=DataType.TEXT),
#                 Property(name="source_pdf",      data_type=DataType.TEXT),
#                 Property(name="source_url",      data_type=DataType.TEXT),
#                 Property(name="chunk_index",     data_type=DataType.INT),
#                 Property(name="total_chunks",    data_type=DataType.INT),
#             ],
#         )
#         logger.info(f"Collection '{COLLECTION_NAME}' created ✅")

#     def load(self) -> "VectorStore":
#         """Connect to an existing collection at query time."""
#         if not self._client.collections.exists(COLLECTION_NAME):
#             raise FileNotFoundError(
#                 f"Weaviate collection '{COLLECTION_NAME}' does not exist.\n"
#                 "Run: python scripts/build_vector_index.py"
#             )
#         self._collection = self._client.collections.get(COLLECTION_NAME)
#         self._total = (
#             self._collection.aggregate
#             .over_all(total_count=True)
#             .total_count
#         )
#         logger.info(
#             f"Weaviate collection '{COLLECTION_NAME}' loaded | "
#             f"objects={self._total}"
#         )
#         return self

#     # ── Indexing ──────────────────────────────────────────────────────────

#     def add(self, chunks: List[TextChunk], embeddings) -> None:
#         """
#         Insert chunks + their embeddings into Weaviate in batch.

#         Args:
#             chunks:     TextChunk objects (carry all metadata).
#             embeddings: np.ndarray shape (N, dimension).
#         """
#         assert len(chunks) == len(embeddings), "chunks/embeddings length mismatch"

#         logger.info(f"Inserting {len(chunks)} objects into Weaviate …")

#         with self._collection.batch.dynamic() as batch:
#             for chunk, vector in zip(chunks, embeddings):
#                 batch.add_object(
#                     properties={
#                         "text":           chunk.text,
#                         "act_name":       chunk.act_name,
#                         "act_year":       int(chunk.act_year),
#                         "section_number": str(chunk.section_number),
#                         "section_title":  chunk.section_title,
#                         "domain":         chunk.domain,
#                         "clause_text":    chunk.clause_text,
#                         "source_pdf":     chunk.source_pdf or "",
#                         "source_url":     chunk.source_url or "",
#                         "chunk_index":    int(chunk.chunk_index),
#                         "total_chunks":   int(chunk.total_chunks),
#                     },
#                     vector=vector.tolist(),
#                 )

#         self._total = (
#             self._collection.aggregate
#             .over_all(total_count=True)
#             .total_count
#         )
#         logger.info(f"Insert complete ✅ | Total in Weaviate: {self._total}")

#     # ── Search ────────────────────────────────────────────────────────────

#     def search(
#         self,
#         query_vector,
#         top_k: int = settings.top_k_retrieval,
#     ) -> List[Tuple[dict, float]]:
#         """
#         Nearest-neighbour vector search.

#         Args:
#             query_vector: np.ndarray shape (dimension,).
#             top_k:        Number of results.

#         Returns:
#             List of (metadata_dict, certainty_score) tuples.
#             certainty is 0.0–1.0 (1.0 = perfect match).
#         """
#         response = self._collection.query.near_vector(
#             near_vector=query_vector.tolist(),
#             limit=top_k,
#             return_metadata=MetadataQuery(distance=True, certainty=True),
#         )

#         results = []
#         for obj in response.objects:
#             meta = dict(obj.properties)
#             score = obj.metadata.certainty or 0.0
#             results.append((meta, float(score)))

#         logger.info(f"Weaviate search → {len(results)} results")
#         return results

#     # ── Context manager ───────────────────────────────────────────────────

#     def __enter__(self) -> "VectorStore":
#         self.connect()
#         return self

#     def __exit__(self, *_) -> None:
#         self.disconnect()

#     @property
#     def total_vectors(self) -> int:
#         return self._total

"""
vector_store.py  (FAISS backend)
─────────────────────────────────
Local FAISS vector store — no internet, no expiry, permanent on disk.

Stores:
    data/faiss_index           ← binary vector index
    data/faiss_metadata.json   ← parallel metadata list

Interface is identical to the Weaviate version so nothing else changes.
"""

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np

from backend.config import settings
from backend.text_processor import TextChunk
from utils.logger import logger

# ── Paths ─────────────────────────────────────────────────────────────────────
INDEX_PATH    = Path("./data/faiss_index")
METADATA_PATH = Path("./data/faiss_metadata.json")


class VectorStore:
    """
    FAISS-backed vector store with JSON metadata side-car.

    Usage (indexing):
        store = VectorStore()
        store.connect()
        store.create_collection(dimension=1024)
        store.add(chunks, embeddings)
        store.disconnect()

    Usage (retrieval):
        store = VectorStore()
        store.connect()
        store.load()
        results = store.search(query_vector, top_k=10)
        store.disconnect()
    """

    def __init__(self) -> None:
        self._index: faiss.IndexFlatIP | None = None
        self._metadata: List[dict] = []
        self._total: int = 0
        self._dimension: int = 0

    # ── Connection (no-op for FAISS — kept for interface compatibility) ────────

    def connect(self) -> None:
        """No-op for FAISS. Exists for interface compatibility with Weaviate."""
        logger.info("VectorStore (FAISS) — local mode, no connection needed")

    def disconnect(self) -> None:
        """No-op for FAISS."""
        logger.info("VectorStore (FAISS) — disconnect (no-op)")

    # ── Collection management ─────────────────────────────────────────────────

    def create_collection(self, dimension: int, recreate: bool = False) -> None:
        """
        Initialise a fresh FAISS index in memory.

        Args:
            dimension: Embedding vector dimension (1024 for e5-large).
            recreate:  If True, wipe existing index. Always True during build.
        """
        self._dimension = dimension

        if not recreate and INDEX_PATH.exists():
            logger.info("FAISS index already exists — loading instead of recreating")
            self.load()
            return

        # IndexFlatIP = inner-product (cosine similarity when vectors are L2-normalised)
        self._index    = faiss.IndexFlatIP(dimension)
        self._metadata = []
        self._total    = 0
        logger.info(f"FAISS index created in memory | dimension={dimension}")

    def load(self) -> "VectorStore":
        """Load existing FAISS index and metadata from disk."""
        if not INDEX_PATH.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {INDEX_PATH}.\n"
                "Run: python scripts/build_vector_index.py"
            )

        logger.info(f"Loading FAISS index from {INDEX_PATH} …")
        self._index = faiss.read_index(str(INDEX_PATH))
        self._dimension = self._index.d

        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            self._metadata = json.load(f)

        self._total = self._index.ntotal
        logger.info(
            f"FAISS index loaded | vectors={self._total} | dimension={self._dimension}"
        )
        return self

    # ── Indexing ──────────────────────────────────────────────────────────────

    def add(self, chunks: List[TextChunk], embeddings: np.ndarray) -> None:
        """
        Add chunks + embeddings to the FAISS index.

        Args:
            chunks:     TextChunk objects (carry all metadata).
            embeddings: np.ndarray of shape (N, dimension), dtype float32.
        """
        assert len(chunks) == len(embeddings), "chunks/embeddings length mismatch"
        assert self._index is not None, "Call create_collection() before add()"

        logger.info(f"Adding {len(chunks)} vectors to FAISS index …")

        # FAISS expects float32
        vecs = embeddings.astype(np.float32)
        self._index.add(vecs)

        # Store metadata in parallel list (index position = FAISS id)
        for chunk in chunks:
            self._metadata.append(asdict(chunk))

        self._total = self._index.ntotal

        # Persist to disk immediately
        self._save()
        logger.info(f"FAISS insert complete ✅ | Total vectors: {self._total}")

    def _save(self) -> None:
        """Persist FAISS index and metadata to disk."""
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(INDEX_PATH))
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(self._metadata, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved → {INDEX_PATH} + {METADATA_PATH}")

    # ── Search ────────────────────────────────────────────────────────────────

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = settings.top_k_retrieval,
    ) -> List[Tuple[dict, float]]:
        """
        Nearest-neighbour search.

        Args:
            query_vector: np.ndarray of shape (dimension,), dtype float32.
            top_k:        Number of results.

        Returns:
            List of (metadata_dict, score) tuples, score = cosine similarity.
        """
        assert self._index is not None, "Call load() before search()"

        q = query_vector.reshape(1, -1).astype(np.float32)
        scores, indices = self._index.search(q, top_k)

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx == -1:       # FAISS padding when ntotal < top_k
                continue
            results.append((self._metadata[idx], float(score)))

        logger.info(f"FAISS search → {len(results)} results")
        return results

    # ── Context manager ───────────────────────────────────────────────────────

    def __enter__(self) -> "VectorStore":
        self.connect()
        return self

    def __exit__(self, *_) -> None:
        self.disconnect()

    @property
    def total_vectors(self) -> int:
        return self._total