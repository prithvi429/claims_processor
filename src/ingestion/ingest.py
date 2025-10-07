import os
import shutil
from datetime import datetime
from pathlib import Path
from src.utils.logging import logger


def ingest_document(file_path: Path) -> Path:
    """
    Ingest a document (PDF, PNG, JPG) and copy it to the raw data directory.
    Adds a timestamp to prevent duplicate overwrites.

    Args:
        file_path (Path): Path to the input document.

    Returns:
        Path: Path to the ingested (copied) file inside data/raw/
    """

    # Validate input path
    if not file_path.exists():
        logger.error(f"❌ File not found for ingestion: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check allowed formats
    allowed_ext = [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]
    if file_path.suffix.lower() not in allowed_ext:
        logger.warning(f"⚠️ Unsupported file type: {file_path.suffix}. Proceeding anyway.")

    # Define target directory (data/raw/)
    base_dir = Path(__file__).resolve().parents[2]  # project root
    target_dir = base_dir / "data" / "raw"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    target_path = target_dir / target_filename

    # Copy the file to raw data directory
    try:
        shutil.copy(file_path, target_path)
        logger.info(f"📥 Ingested file copied to: {target_path}")
    except Exception as e:
        logger.error(f"❌ Error during ingestion of {file_path}: {e}")
        raise RuntimeError(f"Failed to ingest file: {file_path}") from e

    # Log metadata
    file_size_kb = os.path.getsize(target_path) / 1024
    logger.debug(f"📄 File details: name={target_filename}, size={file_size_kb:.2f} KB")

    return target_path


if __name__ == "__main__":
    # For quick manual test
    sample_file = Path("data/test/mock_claim.txt")
    try:
        result = ingest_document(sample_file)
        print(f"✅ Ingested: {result}")
    except Exception as e:
        print(f"❌ {e}")
