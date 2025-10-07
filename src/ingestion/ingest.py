"""Document ingestion helpers (placeholders)."""
import os


def ingest_file(path: str) -> dict:
    """Simulate ingesting a file and returning metadata."""
    return {
        'path': path,
        'filename': os.path.basename(path),
        'status': 'ingested'
    }
