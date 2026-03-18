"""
context_builder.py
──────────────────
Assembles the prompt context block that is injected into the Gemini prompt.

The context block contains the reranked law sections formatted so that
Gemini can accurately cite them in its answer.
"""

from dataclasses import dataclass
from typing import List, Tuple

from utils.logger import logger


@dataclass
class LegalReference:
    """A clean, display-ready representation of a retrieved law section."""
    act_name: str
    act_year: int
    section_number: str
    section_title: str
    clause_text: str
    domain: str
    relevance_score: float
    source_pdf: str = ""
    source_url: str = ""


class ContextBuilder:
    """
    Converts reranked (metadata, score) tuples into:
      1. A structured prompt context string for the LLM.
      2. A list of LegalReference objects for the frontend to display.

    Usage:
        builder = ContextBuilder()
        context_str, references = builder.build(reranked_docs)
    """

    CONTEXT_TEMPLATE = (
        "LEGAL REFERENCE {idx}:\n"
        "  Act          : {act_name} ({act_year})\n"
        "  Section      : {section_number} – {section_title}\n"
        "  Domain       : {domain}\n"
        "  Clause Text  :\n"
        "    {clause_text}\n"
    )

    def build(
        self,
        reranked_docs: List[Tuple[dict, float]],
    ) -> Tuple[str, List[LegalReference]]:
        """
        Build the context string and structured references.

        Args:
            reranked_docs: Output from Reranker.rerank().

        Returns:
            (context_string, list_of_LegalReference)
        """
        references: List[LegalReference] = []
        context_parts: List[str] = []

        for idx, (meta, score) in enumerate(reranked_docs, start=1):
            ref = LegalReference(
                act_name=meta.get("act_name", "Unknown Act"),
                act_year=meta.get("act_year", 0),
                section_number=meta.get("section_number", "?"),
                section_title=meta.get("section_title", ""),
                clause_text=meta.get("clause_text", ""),
                domain=meta.get("domain", ""),
                relevance_score=round(score, 4),
                source_pdf=meta.get("source_pdf", ""),
                source_url=meta.get("source_url", ""),
            )
            references.append(ref)

            block = self.CONTEXT_TEMPLATE.format(
                idx=idx,
                act_name=ref.act_name,
                act_year=ref.act_year,
                section_number=ref.section_number,
                section_title=ref.section_title,
                domain=ref.domain,
                clause_text=ref.clause_text,
            )
            context_parts.append(block)

        context_string = "\n".join(context_parts)
        logger.info(
            f"ContextBuilder: assembled {len(references)} legal references "
            f"({len(context_string)} chars)"
        )
        return context_string, references