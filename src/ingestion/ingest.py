import os
import shutil
from pathlib import Path
from ..config import DATA_DIR
from ..utils.logging import logger

def ingest_document(file_path):
    """
    Simulate ingestion: Copy file to raw storage (data/raw/).
    In production: Upload to S3/Kafka, capture metadata.
    """
    raw_dir = Path(DATA_DIR) / "raw"
    raw_dir.mkdir(exist_ok=True)
    
    filename = file_path.name
    raw_path = raw_dir / f"ingested_{filename}"
    
    try:
        shutil.copy2(file_path, raw_path)
        logger.info(f"Ingested: {file_path} -> {raw_path}")
        # Add metadata (e.g., timestamp)
        metadata = {
            "ingested_at": str(os.path.getctime(file_path)),
            "original_size": os.path.getsize(file_path)
        }
        logger.info(f"Metadata: {metadata}")
        return raw_path
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise