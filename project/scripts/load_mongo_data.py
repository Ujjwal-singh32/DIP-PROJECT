"""
scripts/load_mongo_data.py
──────────────────────────
Loads law sections into MongoDB from:
  • A JSON  file  (.json  — top-level array of objects)
  • A JSONL file  (.jsonl — one JSON object per line)
  • A CSV  file   (.csv   — headers must match schema)
  • Built-in 17 sample rows if no --file is given

Usage:
  python scripts/load_mongo_data.py                          # 17 sample rows
  python scripts/load_mongo_data.py --file data/laws.json    # full JSON array
  python scripts/load_mongo_data.py --file data/laws.jsonl   # JSONL
  python scripts/load_mongo_data.py --file data/laws.csv     # CSV
  python scripts/load_mongo_data.py --file data/laws.json --clear  # wipe first
"""

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient

from backend.config import settings
from utils.logger import logger

# ─── Required fields per document ────────────────────────────────────────────

REQUIRED_FIELDS = {
    "act_name",
    "act_year",
    "clause_text",
    "domain",
    "section_number",
    "section_title",
}

# ─── Built-in sample data (17 rows, used when no --file is given) ─────────────

SAMPLE_DATA = [
    {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "act_year": 2023,
        "section_number": "303",
        "section_title": "Theft",
        "domain": "criminal_law",
        "clause_text": (
            "Whoever, intending to take dishonestly any movable property out of the "
            "possession of any person without that person's consent, moves that property "
            "in order to such taking, is said to commit theft. "
            "Whoever commits theft shall be punished with rigorous imprisonment for a "
            "term which may extend to three years, and shall also be liable to fine."
        ),
        "source_pdf": "BNS_2023.pdf",
        "source_url": "https://legislative.gov.in/sites/default/files/2023-12/20238.pdf",
    },
    {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "act_year": 2023,
        "section_number": "304",
        "section_title": "Theft in dwelling house",
        "domain": "criminal_law",
        "clause_text": (
            "Whoever commits theft in any building, tent or vessel, which building, "
            "tent or vessel is used as a human dwelling, or used for the custody of "
            "property, shall be punished with rigorous imprisonment for a term which "
            "may extend to seven years, and shall also be liable to fine."
        ),
        "source_pdf": "BNS_2023.pdf",
        "source_url": "https://legislative.gov.in/sites/default/files/2023-12/20238.pdf",
    },
    {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "act_year": 2023,
        "section_number": "309",
        "section_title": "Attempt to commit robbery",
        "domain": "criminal_law",
        "clause_text": (
            "Whoever makes any attempt to commit robbery shall be punished with "
            "rigorous imprisonment for a term which may extend to seven years, "
            "and shall also be liable to fine."
        ),
        "source_pdf": "BNS_2023.pdf",
        "source_url": "https://legislative.gov.in/sites/default/files/2023-12/20238.pdf",
    },
    {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "act_year": 2023,
        "section_number": "101",
        "section_title": "Murder",
        "domain": "criminal_law",
        "clause_text": (
            "Except in the cases hereinafter excepted, culpable homicide is murder, if "
            "the act by which the death is caused is done with the intention of causing "
            "death. Whoever commits murder shall be punished with death or imprisonment "
            "for life, and shall also be liable to fine."
        ),
        "source_pdf": "BNS_2023.pdf",
        "source_url": "https://legislative.gov.in/sites/default/files/2023-12/20238.pdf",
    },
    {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "act_year": 2023,
        "section_number": "28",
        "section_title": "Consent known to be given under fear or misconception",
        "domain": "criminal_law",
        "clause_text": (
            "A consent is not such a consent as is intended by any section of this "
            "Sanhita, if the consent is given by a person under fear of injury, or "
            "under a misconception of fact, and if the person doing the act knows, or "
            "has reason to believe, that the consent was given in consequence of such "
            "fear or misconception."
        ),
        "source_pdf": "BNS_2023.pdf",
        "source_url": "https://legislative.gov.in/sites/default/files/2023-12/20238.pdf",
    },
    {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "act_year": 2023,
        "section_number": "64",
        "section_title": "Punishment for rape",
        "domain": "criminal_law",
        "clause_text": (
            "Whoever commits rape shall be punished with rigorous imprisonment of either "
            "description for a term which shall not be less than ten years, but which may "
            "extend to imprisonment for life, and shall also be liable to fine."
        ),
        "source_pdf": "BNS_2023.pdf",
        "source_url": "https://legislative.gov.in/sites/default/files/2023-12/20238.pdf",
    },
    {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "act_year": 2023,
        "section_number": "316",
        "section_title": "Criminal breach of trust",
        "domain": "criminal_law",
        "clause_text": (
            "Whoever, being in any manner entrusted with property, or with any dominion "
            "over property, dishonestly misappropriates or converts to his own use that "
            "property commits criminal breach of trust and shall be punished with "
            "imprisonment of either description for a term which may extend to five years, "
            "or with fine, or with both."
        ),
        "source_pdf": "BNS_2023.pdf",
        "source_url": "https://legislative.gov.in/sites/default/files/2023-12/20238.pdf",
    },
    {
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "act_year": 2023,
        "section_number": "318",
        "section_title": "Cheating",
        "domain": "criminal_law",
        "clause_text": (
            "Whoever, by deceiving any person, fraudulently or dishonestly induces the "
            "person so deceived to deliver any property to any person is said to cheat. "
            "Whoever cheats shall be punished with imprisonment of either description "
            "for a term which may extend to three years, or with fine, or with both."
        ),
        "source_pdf": "BNS_2023.pdf",
        "source_url": "https://legislative.gov.in/sites/default/files/2023-12/20238.pdf",
    },
    {
        "act_name": "Indian Contract Act, 1872",
        "act_year": 1872,
        "section_number": "10",
        "section_title": "What agreements are contracts",
        "domain": "contract_law",
        "clause_text": (
            "All agreements are contracts if they are made by the free consent of "
            "parties competent to contract, for a lawful consideration and with a "
            "lawful object, and are not hereby expressly declared to be void."
        ),
        "source_pdf": "IndianContractAct_1872.pdf",
        "source_url": "https://indiankanoon.org/doc/1877750/",
    },
    {
        "act_name": "Indian Contract Act, 1872",
        "act_year": 1872,
        "section_number": "2(h)",
        "section_title": "Definition of Contract",
        "domain": "contract_law",
        "clause_text": "An agreement enforceable by law is a contract.",
        "source_pdf": "IndianContractAct_1872.pdf",
        "source_url": "https://indiankanoon.org/doc/1877750/",
    },
    {
        "act_name": "Indian Contract Act, 1872",
        "act_year": 1872,
        "section_number": "13",
        "section_title": "Consent - definition",
        "domain": "contract_law",
        "clause_text": (
            "Two or more persons are said to consent when they agree upon the same "
            "thing in the same sense."
        ),
        "source_pdf": "IndianContractAct_1872.pdf",
        "source_url": "https://indiankanoon.org/doc/1877750/",
    },
    {
        "act_name": "Indian Contract Act, 1872",
        "act_year": 1872,
        "section_number": "73",
        "section_title": "Compensation for loss or damage caused by breach of contract",
        "domain": "contract_law",
        "clause_text": (
            "When a contract has been broken, the party who suffers by such breach is "
            "entitled to receive compensation for any loss or damage caused to him "
            "thereby, which naturally arose in the usual course of things from such breach."
        ),
        "source_pdf": "IndianContractAct_1872.pdf",
        "source_url": "https://indiankanoon.org/doc/1877750/",
    },
    {
        "act_name": "Information Technology Act, 2000",
        "act_year": 2000,
        "section_number": "43",
        "section_title": "Penalty and compensation for damage to computer",
        "domain": "cyber_law",
        "clause_text": (
            "If any person without permission of the owner or any other person who is "
            "incharge of a computer, computer system or computer network, accesses or "
            "secures access to such computer, he shall be liable to pay damages by way "
            "of compensation to the person so affected."
        ),
        "source_pdf": "IT_Act_2000.pdf",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },
    {
        "act_name": "Information Technology Act, 2000",
        "act_year": 2000,
        "section_number": "66",
        "section_title": "Computer related offences",
        "domain": "cyber_law",
        "clause_text": (
            "If any person, dishonestly or fraudulently, does any act referred to in "
            "section 43, he shall be punishable with imprisonment for a term which may "
            "extend to three years or with fine which may extend to five lakh rupees or "
            "with both."
        ),
        "source_pdf": "IT_Act_2000.pdf",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },
    {
        "act_name": "Consumer Protection Act, 2019",
        "act_year": 2019,
        "section_number": "2(7)",
        "section_title": "Definition of Consumer",
        "domain": "consumer_law",
        "clause_text": (
            "'Consumer' means any person who buys any goods for a consideration which "
            "has been paid or promised or partly paid and partly promised, or under any "
            "system of deferred payment."
        ),
        "source_pdf": "ConsumerProtectionAct_2019.pdf",
        "source_url": "https://consumeraffairs.nic.in/",
    },
    {
        "act_name": "Consumer Protection Act, 2019",
        "act_year": 2019,
        "section_number": "35",
        "section_title": "Complaint before District Commission",
        "domain": "consumer_law",
        "clause_text": (
            "A complaint in relation to any goods sold or delivered or any service "
            "provided may be filed with a District Commission by the consumer to whom "
            "such goods are sold or delivered or such service is provided."
        ),
        "source_pdf": "ConsumerProtectionAct_2019.pdf",
        "source_url": "https://consumeraffairs.nic.in/",
    },
    {
        "act_name": "Information Technology Act, 2000",
        "act_year": 2000,
        "section_number": "66A",
        "section_title": "Punishment for sending offensive messages",
        "domain": "cyber_law",
        "clause_text": (
            "Any person who sends, by means of a computer resource or a communication "
            "device, any information that is grossly offensive or has menacing character "
            "shall be punishable with imprisonment for a term which may extend to three "
            "years and with fine."
        ),
        "source_pdf": "IT_Act_2000.pdf",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/1999",
    },
]


# ─── File loaders ─────────────────────────────────────────────────────────────

def load_json_file(path: Path) -> list[dict]:
    """Load a .json file — must be a top-level array of objects."""
    logger.info(f"Reading JSON: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON array at the top level, got {type(data).__name__}.\n"
            "Your file should look like: [ {{...}}, {{...}}, ... ]"
        )
    logger.info(f"  → {len(data)} records found in JSON file")
    return data


def load_jsonl_file(path: Path) -> list[dict]:
    """Load a .jsonl file — one JSON object per line."""
    logger.info(f"Reading JSONL: {path}")
    records = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                logger.warning(f"  Line {lineno} skipped (invalid JSON): {exc}")
    logger.info(f"  → {len(records)} records found in JSONL file")
    return records


def load_csv_file(path: Path) -> list[dict]:
    """
    Load a .csv file.

    Required columns: act_name, act_year, clause_text, domain,
                      section_number, section_title
    Optional columns: source_pdf, source_url
    """
    logger.info(f"Reading CSV: {path}")
    records = []
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        headers = set(reader.fieldnames or [])

        # Check required columns exist
        missing_cols = REQUIRED_FIELDS - headers
        if missing_cols:
            raise ValueError(
                f"CSV is missing required columns: {missing_cols}\n"
                f"Columns found: {sorted(headers)}\n\n"
                "Required columns: act_name, act_year, clause_text, "
                "domain, section_number, section_title"
            )

        for row in reader:
            try:
                row["act_year"] = int(row["act_year"])
            except (ValueError, KeyError):
                row["act_year"] = 0
            records.append(dict(row))

    logger.info(f"  → {len(records)} records found in CSV file")
    return records


def load_file(path: Path) -> list[dict]:
    """Dispatch to the correct loader based on file extension."""
    suffix = path.suffix.lower()
    loaders = {".json": load_json_file, ".jsonl": load_jsonl_file, ".csv": load_csv_file}
    if suffix not in loaders:
        raise ValueError(
            f"Unsupported file extension '{suffix}'.\n"
            "Accepted: .json, .jsonl, .csv"
        )
    return loaders[suffix](path)


# ─── Validation ───────────────────────────────────────────────────────────────

def validate_record(record: dict, index: int) -> dict | None:
    """Return a cleaned record, or None if required fields are missing."""
    missing = REQUIRED_FIELDS - set(record.keys())
    if missing:
        logger.warning(
            f"Record #{index} skipped — missing fields: {missing} | "
            f"act={record.get('act_name', '?')} §{record.get('section_number', '?')}"
        )
        return None

    # Coerce act_year
    try:
        record["act_year"] = int(record["act_year"])
    except (TypeError, ValueError):
        record["act_year"] = 0

    # Strip whitespace
    for field in ("act_name", "section_title", "clause_text"):
        if isinstance(record.get(field), str):
            record[field] = record[field].strip()

    return record


# ─── MongoDB upsert ───────────────────────────────────────────────────────────

def upsert_records(collection, records: list[dict]) -> tuple[int, int, int]:
    """
    Upsert all records.  Key = (act_name, section_number).
    Returns (new_inserts, updates, skipped).
    """
    inserted = updated = skipped = 0

    for i, raw in enumerate(records, 1):
        record = validate_record(dict(raw), i)
        if record is None:
            skipped += 1
            continue

        result = collection.update_one(
            {
                "act_name": record["act_name"],
                "section_number": str(record["section_number"]),
            },
            {"$set": record},
            upsert=True,
        )

        if result.upserted_id:
            inserted += 1
        elif result.modified_count:
            updated += 1

        # Progress log every 50 records
        if i % 50 == 0:
            logger.info(f"  … {i}/{len(records)} processed")

    return inserted, updated, skipped


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Load Indian law sections into MongoDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
File format requirements
────────────────────────
JSON  (.json):  Top-level array of objects.
JSONL (.jsonl): One JSON object per line.
CSV   (.csv):   Header row with these columns:
                act_name, act_year, clause_text, domain,
                section_number, section_title
                (source_pdf and source_url are optional)

Examples
────────
  python scripts/load_mongo_data.py
  python scripts/load_mongo_data.py --file data/bns_sections.json
  python scripts/load_mongo_data.py --file data/all_laws.csv
  python scripts/load_mongo_data.py --file data/laws.json --clear
        """,
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to your data file (.json / .jsonl / .csv). "
             "Omit to insert 17 built-in sample rows.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Drop the entire collection before inserting. WARNING: irreversible.",
    )
    args = parser.parse_args()

    # ── Choose data source ────────────────────────────────────────────────
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(
                f"File not found: {file_path.resolve()}\n"
                "Double-check the path and try again."
            )
            sys.exit(1)
        records = load_file(file_path)
    else:
        records = SAMPLE_DATA
        logger.info(
            f"No --file argument given.\n"
            f"Using {len(records)} built-in sample rows.\n"
            f"To load your full dataset run:\n"
            f"  python scripts/load_mongo_data.py --file <your_file.json|.jsonl|.csv>"
        )

    if not records:
        logger.error("No records to insert. Check your file content.")
        sys.exit(1)

    # ── Connect ───────────────────────────────────────────────────────────
    logger.info(f"Connecting to MongoDB: {settings.mongodb_uri}")
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5_000)
    try:
        client.admin.command("ping")
        logger.info("MongoDB connection OK")
    except Exception as exc:
        logger.error(f"Cannot connect to MongoDB: {exc}")
        sys.exit(1)

    db = client[settings.mongo_db_name]
    collection = db[settings.mongo_collection]

    # ── Optional wipe ─────────────────────────────────────────────────────
    if args.clear:
        before = collection.count_documents({})
        collection.drop()
        logger.warning(
            f"--clear flag: dropped '{settings.mongo_collection}' ({before} docs deleted)"
        )

    # ── Unique index ──────────────────────────────────────────────────────
    collection.create_index(
        [("act_name", 1), ("section_number", 1)],
        unique=True,
        name="unique_section",
    )

    # ── Upsert ────────────────────────────────────────────────────────────
    logger.info(f"Starting upsert of {len(records)} records …")
    inserted, updated, skipped = upsert_records(collection, records)
    total = collection.count_documents({})

    logger.info(
        f"\n{'─'*48}\n"
        f"  ✅  Done!\n"
        f"  New inserts  : {inserted}\n"
        f"  Updated      : {updated}\n"
        f"  Skipped (bad): {skipped}\n"
        f"  Total in DB  : {total}\n"
        f"{'─'*48}\n"
        f"Next step → python scripts/build_vector_index.py"
    )
    client.close()


if __name__ == "__main__":
    main()