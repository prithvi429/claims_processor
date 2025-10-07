import sqlite3
from datetime import datetime, timedelta
from ..config import CONFIDENCE_THRESHOLD, MAX_CLAIM_AMOUNT, DATABASE_URL
from ..utils.logging import logger

def validate_and_review(processed):
    """
    Apply business rules, check confidence, flag for HITL.
    Updates processed["status"] and stores in DB if needed.
    """
    errors = []
    confidence = processed.get("confidence", 0.0)
    
    # Rule: Amount limit
    if processed.get("claim_amount", 0) > MAX_CLAIM_AMOUNT:
        errors.append("Amount exceeds policy limit")
    
    # Rule: Date within window (assume current date as reference)
    incident_date = processed.get("incident_date")
    if incident_date:
        try:
            inc_date = datetime.fromisoformat(incident_date)
            if datetime.now() - inc_date > timedelta(days=30):  # Example: 30-day filing window
                errors.append("Incident date outside filing window")
        except ValueError:
            errors.append("Invalid date format")
    else:
        errors.append("Missing incident date")
    
    # Confidence check
    if confidence < CONFIDENCE_THRESHOLD or errors:
        processed["status"] = "review"
        # Store for HITL
        store_for_hitl(processed, errors)
        logger.warning(f"Flagged for review: {processed['claim_id']} - Errors: {errors}")
    else:
        processed["status"] = "ready_for_approval"
        logger.info(f"Auto-approved: {processed['claim_id']}")
    
    return processed

def store_for_hitl(processed, errors):
    """Store low-confidence claims in SQLite for HITL."""
    conn = sqlite3.connect(DATABASE_URL.replace("sqlite:///", ""))  # Adjust for path
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            claim_id TEXT PRIMARY KEY,
            extracted_data TEXT,
            confidence REAL,
            status TEXT,
            review_notes TEXT
        )
    """)
    cursor.execute("""
        INSERT OR REPLACE INTO claims 
        VALUES (?, ?, ?, ?, ?)
    """, (
        processed["claim_id"],
        json.dumps(processed),
        processed["confidence"],
        processed["status"],
        "; ".join(errors)
    ))
    conn.commit()
    conn.close()