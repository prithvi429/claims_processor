import argparse
import json
from pathlib import Path
from src.config import DATA_DIR, CLAIM_SCHEMA
from src.ingestion.ingest import ingest_document
from src.extraction.parser import extract_text
from src.processing.genai import process_with_genai
from src.validation.validator import validate_and_review
from src.storage.output import store_output
from src.utils.logging import logger


def main():
    parser = argparse.ArgumentParser(description="🧠 Intelligent Claims Processing System")
    parser.add_argument("--input", required=True, help="Path to PDF/Image file")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"❌ Input file not found: {input_path}")
        exit(1)

    logger.info(f"🚀 Starting processing for: {input_path}")

    try:
        # Step 1: Ingest document
        raw_path = ingest_document(input_path)
        logger.info("📥 Document ingested successfully.")

        # Step 2: Extract text
        extracted = extract_text(input_path)
        logger.info("📝 Text extraction complete.")

        # Step 3: Process using GenAI + NLP
        processed = process_with_genai(extracted)
        logger.info("🤖 Generative AI processing done.")

        # Step 4: Validate and flag for review if needed
        validated = validate_and_review(processed)
        logger.info("✅ Validation and review completed.")

        # Step 5: Store the result
        output_path = store_output(validated, raw_path)
        logger.info(f"💾 Output saved successfully at: {output_path}")

        # Print structured output (for console/CI visibility)
        print(json.dumps(validated, indent=2))

    except Exception as e:
        logger.exception(f"❌ Error processing {input_path}: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
