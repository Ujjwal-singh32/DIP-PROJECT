"""
text_processor.py
─────────────────
Converts raw LawSection documents into text chunks suitable for embedding.

Pipeline per document:
  1. Compose a structured text from metadata + clause text.
  2. If the text exceeds CHUNK_SIZE tokens, split with overlap.
  3. Return a list of TextChunk objects carrying the metadata forward.
"""

from dataclasses import dataclass, field
from typing import List

from backend.config import settings
from backend.mongo_loader import LawSection
from utils.helpers import clean_text
from utils.logger import logger


# ─── Output data structure ───────────────────────────────────────────────────

@dataclass
class TextChunk:
    """A single embeddable unit derived from a law section."""

    # The text to be embedded
    text: str

    # Provenance metadata (preserved through chunking)
    act_name: str
    act_year: int
    section_number: str
    section_title: str
    domain: str
    clause_text: str            # full original clause (for display)
    source_pdf: str = ""
    source_url: str = ""

    # For multi-chunk sections
    chunk_index: int = 0
    total_chunks: int = 1


# ─── Processor ───────────────────────────────────────────────────────────────

class TextProcessor:
    """
    Transforms LawSection objects into TextChunk lists.

    The 'structured text' format is optimised for e5-large / InLegalBERT
    retrieval — both models benefit from explicit field labelling.
    """

    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
    ) -> None:
        self.chunk_size = chunk_size          # approx characters (not tokens)
        self.chunk_overlap = chunk_overlap

    # ── Text composition ──────────────────────────────────────────────────

    @staticmethod
    def _compose(section: LawSection) -> str:
        """
        Build the canonical structured text for a law section.

        Format keeps field names explicit so the embedding model can
        leverage section-level semantics during retrieval.
        """
        return (
            f"Act: {section.act_name} ({section.act_year})\n"
            f"Section {section.section_number}: {section.section_title}\n"
            f"Domain: {section.domain}\n"
            f"Text: {clean_text(section.clause_text)}"
        )

    # ── Chunking ──────────────────────────────────────────────────────────

    def _split(self, text: str) -> List[str]:
        """
        Split `text` into overlapping character-level chunks.
        Simple character splitting is used here; swap for a tiktoken-based
        splitter if token-exact chunking is required.
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks: List[str] = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            # Advance, stepping back by overlap so context is shared
            start += self.chunk_size - self.chunk_overlap
            if start >= len(text):
                break
        return chunks

    # ── Public API ────────────────────────────────────────────────────────

    def process(self, section: LawSection) -> List[TextChunk]:
        """Convert a single LawSection into one or more TextChunks."""
        full_text = self._compose(section)
        raw_chunks = self._split(full_text)
        total = len(raw_chunks)

        return [
            TextChunk(
                text=chunk_text,
                act_name=section.act_name,
                act_year=section.act_year,
                section_number=section.section_number,
                section_title=section.section_title,
                domain=section.domain,
                clause_text=section.clause_text,       # always full text
                source_pdf=section.source_pdf or "",
                source_url=section.source_url or "",
                chunk_index=idx,
                total_chunks=total,
            )
            for idx, chunk_text in enumerate(raw_chunks)
        ]

    def process_all(self, sections: List[LawSection]) -> List[TextChunk]:
        """Process an entire list of LawSections."""
        all_chunks: List[TextChunk] = []
        for section in sections:
            chunks = self.process(section)
            all_chunks.extend(chunks)

        logger.info(
            f"TextProcessor: {len(sections)} sections → {len(all_chunks)} chunks "
            f"(chunk_size={self.chunk_size}, overlap={self.chunk_overlap})"
        )
        return all_chunks