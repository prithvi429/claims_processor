import sqlite3
import json
from ..config import DATABASE_URL
from ..utils.logging import logger

def query_hitl(status="review"):
    """
    Query low-confidence claims from DB for human review.
    Returns list of dicts.
    """
    conn = sqlite3.connect(DATABASE_URL.replace("sqlite:///", ""))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM claims WHERE status=?", (status,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        claim_data = json.loads(row[1])  # extracted_data
        results.append({
            "claim_id": row[0],
            "data": claim_data,
            "confidence": row[2],
            "status": row[3],
            "notes": row[4]
        })
    
    logger.info(f"Queried {len(results)} HITL items")
    return results

# Example usage: In a UI or script
# hitl_items = query_hitl()
# for item in hitl_items:
#     print(item)