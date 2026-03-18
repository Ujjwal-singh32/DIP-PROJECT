"""
scripts/check_mongo.py
──────────────────────
Check MongoDB connection and display basic stats.

Usage:
  python scripts/check_mongo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient
from backend.config import settings
from utils.logger import logger


def main():
    logger.info(f"Connecting to MongoDB: {settings.mongo_uri}")
    client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5_000)
    try:
        client.admin.command("ping")
        logger.info("✅ MongoDB connection OK")

        # Get database info
        db = client[settings.mongo_db_name]
        collections = db.list_collection_names()
        logger.info(f"Database: {settings.mongo_db_name}")
        logger.info(f"Collections: {collections}")

        # Check the main collection
        collection = db[settings.mongo_collection]
        count = collection.count_documents({})
        logger.info(f"Documents in '{settings.mongo_collection}': {count}")

        if count > 0:
            # Show a sample document
            sample = collection.find_one()
            logger.info(f"Sample document keys: {list(sample.keys()) if sample else 'None'}")

    except Exception as exc:
        logger.error(f"❌ Cannot connect to MongoDB: {exc}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()