"""
src/storage/hitl.py
--------------------------------
Implements Human-In-The-Loop (HITL) data storage.
Stores claims with low confidence or failed validations into SQLite database.
"""

import os
import sqlite3
from pathlib import Path
from typing import List
from src.config import DATABASE_URL
from src.utils.logging import logger

# ---------------------------------------------------------------------
# Initialize SQLite database (simple file-based storage for HITL review)
# ---------------------------------------------------------------------

# Extract database path from DATABASE_URL (example: sqlite:///db/claims.db)
if DATABASE_URL.startswith("sqlite:///"):
    DB_PATH = DATABASE_URL.replace("sqlite:///", "")
else:
    DB_PATH = "db/claims.db"

DB_PATH = Path(DB_PATH)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _connect():
    """Create a database connection."""
    return sqlite3.connect(DB_PATH)


def _init_db():
    """Initialize the HITL table if not exists."""
    try:
        with _connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS hitl_claims (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    claim_id TEXT,
                    amount REAL,
                    claim_date TEXT,
                    errors TEXT,
                    status TEXT DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        logger.info(f"✅ HITL table ready at {DB_PATH}")
    except Exception as e:
        logger.exception(f"❌ Failed to initialize HITL DB: {e}")


# Initialize database at import
_init_db()


# ---------------------------------------------------------------------
# Main function for validator to call
# ---------------------------------------------------------------------
def insert_hitl_record(claim_id: str, amount: float, claim_date: str, errors: List[str]):
    """
    Insert a new record into HITL table for human review.
    """
    try:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO hitl_claims (claim_id, amount, claim_date, errors)
                VALUES (?, ?, ?, ?)
                """,
                (claim_id, amount, claim_date, ", ".join(errors)),
            )
            conn.commit()
        logger.info(f"🧾 Added claim {claim_id} to HITL DB for review.")
    except Exception as e:
        logger.exception(f"❌ Failed to insert HITL record for {claim_id}: {e}")


# ---------------------------------------------------------------------
# Optional: Utility to fetch pending records
# ---------------------------------------------------------------------
def fetch_pending_claims(limit: int = 5):
    """Retrieve a few pending HITL claims for UI or testing."""
    try:
        with _connect() as conn:
            rows = conn.execute(
                "SELECT id, claim_id, amount, claim_date, errors, status FROM hitl_claims WHERE status='Pending' LIMIT ?",
                (limit,),
            ).fetchall()
        return rows
    except Exception as e:
        logger.error(f"Failed to fetch HITL records: {e}")
        return []
