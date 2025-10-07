import argparse
import json
import os
from pathlib import Path

from .config import DATA_DIR, CLAIM_SCHEMA
from .ingestion.ingest import ingest_document
from .extraction.parser import extract_text
from .processing.genai import process_with_genai  # Combines NLP and GenAI
from .validation.validator import validate_and_review
from .storage.output import store_output
from .utils.logging import logger

def main():
    parser = argparse.ArgumentParser(description="Process insurance claim document")
    parser.add_argument("--input", required=True, help="Path to PDF/Image file")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return

    logger.info(f"Starting processing for: {input_path}")

    # Step 1: Ingest
    raw_path = ingest_document(input_path)

    # Step 2: Extract
    extracted = extract_text(input_path)

    # Step 3-4: Process (NLP + GenAI)
    processed = process_with_genai(extracted)

    # Step 5: Validate and Review
    validated = validate_and_review(processed)

    # Step 6: Store
    output_path = store_output(validated, raw_path)

    logger.info(f"Processing complete. Output: {output_path}")
    print(json.dumps(validated, indent=2))  # Print for console

if __name__ == "__main__":
    main()