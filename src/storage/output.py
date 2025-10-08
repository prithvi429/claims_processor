"""
src/storage/output.py
--------------------------------
Handles storage of processed claim results into JSON files or databases.
Ensures safe file naming even if claim_id is missing.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from src.config import DATA_DIR
from src.utils.logging import logger


def store_output(processed: dict, source_path: str) -> str:
    """
    Store the processed claim data as JSON in data/processed directory.
    Generates safe filenames even if 'claim_id' is missing.
    """
    processed_dir = Path(DATA_DIR) / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Safe fallback if claim_id not present
    claim_id = processed.get("claim_id")
    if not claim_id:
        # Create a temporary unique ID based on timestamp
        claim_id = f"temp_{int(datetime.now().timestamp())}"
        logger.warning(f"⚠️ Missing claim_id — using generated ID: {claim_id}")

    # Build output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"processed_{claim_id}_{timestamp}.json"
    output_path = processed_dir / filename

    # Write to JSON file safely
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(processed, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Output stored successfully: {output_path}")
        return str(output_path)
    except Exception as e:
        logger.exception(f"❌ Failed to store output JSON: {e}")
        raise
