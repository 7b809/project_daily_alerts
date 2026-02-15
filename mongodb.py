"""
MongoDB storage layer for Index Early Alerts Project

Optimized structure:
- Only required fields stored
- Flat contracts array
- Duplicate prevention
- Indexed for fast queries
"""

import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv


# -------------------------------------------------------
# LOAD ENV
# -------------------------------------------------------

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "index_alerts")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "daily_snapshots")


# -------------------------------------------------------
# CONNECT
# -------------------------------------------------------

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Create unique index (prevents duplicate date+exchange)
collection.create_index(
    [("date", ASCENDING), ("exchange", ASCENDING)],
    unique=True
)


# -------------------------------------------------------
# TRANSFORM API DATA
# -------------------------------------------------------

def transform_data(data: dict):
    """
    Extract only required fields from API response.
    Converts full API payload into clean lightweight format.
    """

    cleaned_contracts = []

    for symbol, info in data.items():

        cleaned_contracts.append({
            "symbol": symbol,
            "ltp": info.get("ltp"),
            "volume": info.get("volume"),
            "oi": info.get("openInterest"),
            "oi_change": info.get("oiDayChange"),
            "oi_change_perc": info.get("oiDayChangePerc"),
            "timestamp": info.get("lastTradeTime")
        })

    return cleaned_contracts


# -------------------------------------------------------
# SAVE SNAPSHOT
# -------------------------------------------------------

def save_snapshot(date_str: str, exchange: str, data: dict):
    """
    Saves cleaned snapshot into MongoDB.
    Skips if already saved.
    """

    # Check duplicate
    existing = collection.find_one({
        "date": date_str,
        "exchange": exchange
    })

    if existing:
        print(f"[SKIP] {exchange} already saved for {date_str}")
        return

    # Clean data
    cleaned_contracts = transform_data(data)

    document = {
        "date": date_str,
        "exchange": exchange,
        "total_contracts": len(cleaned_contracts),
        "contracts": cleaned_contracts,
        "created_at": datetime.utcnow()
    }

    try:
        collection.insert_one(document)
        print(f"[SAVED] {exchange} saved ({len(cleaned_contracts)} contracts)")

    except Exception as e:
        print(f"[ERROR] Mongo insert failed: {e}")
