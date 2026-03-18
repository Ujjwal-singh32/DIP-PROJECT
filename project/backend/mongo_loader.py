"""
mongo_loader.py
───────────────
Loads law section documents from MongoDB and returns them as validated
Pydantic models.  Handles connection pooling and graceful error handling.

Schema is flexible — handles both old schema (with domain) and new schema
(without domain, with source_file/source_act instead of source_pdf/source_url).
"""

import re
from typing import Generator, List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pydantic import BaseModel, Field, field_validator, model_validator

from backend.config import settings
from utils.logger import logger


# ─── Domain auto-detection ───────────────────────────────────────────────────

_DOMAIN_KEYWORDS = {
    "criminal_law":      ["penal", "bns", "ipc", "crpc", "bnss", "criminal", "offence",
                          "punishment", "murder", "theft", "robbery", "assault", "arrest"],
    "cyber_law":         ["information technology", "cyber", "it act", "digital", "computer",
                          "electronic", "internet", "hacking", "data protection"],
    "contract_law":      ["contract", "agreement", "breach", "consideration", "offer",
                          "acceptance", "indemnity", "guarantee", "bailment"],
    "consumer_law":      ["consumer", "deficiency", "service", "goods", "complaint",
                          "district commission", "unfair trade"],
    "constitutional_law":["constitution", "fundamental rights", "directive principles",
                          "parliament", "article", "amendment", "citizen"],
    "property_law":      ["property", "transfer", "mortgage", "lease", "easement",
                          "sale deed", "immovable", "land", "real estate", "rera"],
    "corporate_law":     ["company", "companies", "director", "shareholder", "board",
                          "incorporation", "winding up", "insolvency"],
    "family_law":        ["marriage", "divorce", "custody", "adoption", "maintenance",
                          "hindu", "muslim", "christian", "succession", "inheritance"],
    "labour_law":        ["labour", "labor", "employee", "employer", "wages", "workmen",
                          "factory", "trade union", "industrial dispute"],
    "tax_law":           ["income tax", "gst", "goods and services", "customs", "excise",
                          "tds", "assessment", "taxable"],
    "civil_law":         ["civil procedure", "suit", "decree", "appeal", "revision",
                          "limitation", "specific relief", "injunction"],
    "medical_law":       ["medical", "dentist", "doctor", "hospital", "pharmacy",
                          "clinical", "patient", "health", "nurse", "drug"],
}


def _detect_domain(act_name: str, clause_text: str = "") -> str:
    """Auto-detect domain from act name and clause text."""
    combined = (act_name + " " + clause_text[:200]).lower()
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return domain
    return "general_law"


# ─── Pydantic schema ─────────────────────────────────────────────────────────

class LawSection(BaseModel):
    """
    Validated representation of a single law section from MongoDB.
    Flexible — works with both old and new document schemas.
    """

    act_name:       str
    act_year:       int                    # coerced from str if needed
    clause_text:    str
    section_number: str
    section_title:  str
    domain:         str = "general_law"   # optional — auto-detected if missing
    source_pdf:     Optional[str] = None
    source_url:     Optional[str] = None

    class Config:
        populate_by_name = True
        extra = "ignore"                  # ignore unknown fields like source_file, source_act

    # ── Coerce act_year from string to int ────────────────────────────────
    @field_validator("act_year", mode="before")
    @classmethod
    def coerce_year(cls, v):
        try:
            return int(v)
        except (TypeError, ValueError):
            # Extract 4-digit year from strings like "2001 (amended)"
            match = re.search(r"\d{4}", str(v))
            return int(match.group()) if match else 0

    # ── Auto-detect domain if missing or empty ────────────────────────────
    @model_validator(mode="before")
    @classmethod
    def fill_missing_fields(cls, data: dict) -> dict:
        # Map source_file → source_pdf if source_pdf not present
        if not data.get("source_pdf") and data.get("source_file"):
            data["source_pdf"] = data["source_file"]

        # Map source_act → source_url hint if source_url not present
        if not data.get("source_url") and data.get("source_act"):
            data["source_url"] = ""

        # Auto-detect domain if missing or empty
        if not data.get("domain"):
            data["domain"] = _detect_domain(
                data.get("act_name", ""),
                data.get("clause_text", ""),
            )

        return data


# ─── Loader class ────────────────────────────────────────────────────────────

class MongoLawLoader:
    """
    Connects to MongoDB and streams law section documents.

    Usage:
        loader = MongoLawLoader()
        sections = loader.load_all()
    """

    def __init__(self) -> None:
        self._client: Optional[MongoClient] = None
        self._collection: Optional[Collection] = None

    # ── Connection management ─────────────────────────────────────────────

    def connect(self) -> None:
        """Initialise MongoDB client and validate the connection."""
        logger.info(f"Connecting to MongoDB at {settings.mongodb_uri}")
        self._client = MongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5_000,
            connectTimeoutMS=5_000,
        )
        # Ping to verify connectivity
        self._client.admin.command("ping")
        db = self._client[settings.mongo_db_name]
        self._collection = db[settings.mongo_collection]
        count = self._collection.count_documents({})
        logger.info(
            f"Connected → DB='{settings.mongo_db_name}' "
            f"Collection='{settings.mongo_collection}' "
            f"Documents={count}"
        )

    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")

    # ── Data loading ──────────────────────────────────────────────────────

    def _iter_raw(self, query: dict = {}) -> Generator[dict, None, None]:
        """Yield raw MongoDB documents matching `query`."""
        if self._collection is None:
            raise RuntimeError("Call connect() before loading data.")
        cursor = self._collection.find(query, {"_id": 0})
        yield from cursor

    def load_all(self, domain: Optional[str] = None) -> List[LawSection]:
        """
        Load and validate all documents from the collection.

        Args:
            domain: Optional filter, e.g. 'criminal_law'.

        Returns:
            List of LawSection instances.
        """
        query: dict = {}
        if domain:
            query["domain"] = domain
            logger.info(f"Filtering by domain='{domain}'")

        sections: List[LawSection] = []
        errors = 0

        for raw in self._iter_raw(query):
            try:
                sections.append(LawSection(**raw))
            except Exception as exc:
                errors += 1
                logger.warning(f"Skipping malformed document: {exc} | doc={raw}")

        logger.info(
            f"Loaded {len(sections)} valid sections "
            f"({'all domains' if not domain else domain}) | "
            f"Skipped {errors} malformed docs"
        )
        return sections

    # ── Context manager support ───────────────────────────────────────────

    def __enter__(self) -> "MongoLawLoader":
        self.connect()
        return self

    def __exit__(self, *_) -> None:
        self.disconnect()


# ─── Convenience function ────────────────────────────────────────────────────

def load_law_sections(domain: Optional[str] = None) -> List[LawSection]:
    """Top-level convenience wrapper used by indexing scripts."""
    with MongoLawLoader() as loader:
        return loader.load_all(domain=domain)