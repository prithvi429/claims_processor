import json
import os
from pathlib import Path
from ..config import DATA_DIR
from ..utils.logging import logger

def store_output(processed, raw_path):
    """
    Store processed claim as JSON in data/processed/.
    In prod: Push to PostgreSQL/S3 and trigger workflow.
    """
    processed_dir = Path(DATA_DIR) / "processed"
    processed_dir.mkdir(exist_ok=True)
    
    claim_id = processed["claim_id"]
    output_path = processed_dir / f"processed_{claim_id}.json"
    
    try:
        with open(output_path, "w") as f:
            json.dump(processed, f, indent=2)
        logger.info(f"Stored output: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Storage failed: {e}")
        raise