import argparse
import json
import os
from pathlib import Path
from src.config import DATA_DIR
from src.ingestion.ingest import ingest_document
from src.extraction.parser import extract_text
from src.processing.genai import process_with_genai
from src.validation.validator import validate_and_review
from src.storage.output import store_output
from src.utils.logging import logger

# Supported input file extensions
SUPPORTED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".txt"]


def process_single_file(input_path: Path):
    """
    Process a single claim document end-to-end:
    ingestion → extraction → GenAI → validation → storage
    """
    try:
        logger.info(f"🚀 Starting processing for: {input_path}")

        # Step 1: Ingest
        raw_path = ingest_document(input_path)

        # Step 2: Extract text
        extracted = extract_text(input_path)

        # Step 3: Process with Generative AI (summarization/normalization)
        processed = process_with_genai(extracted)

        # Step 4: Validate extracted/processed data
        validated = validate_and_review(processed)

        # Step 5: Store output JSON
        output_path = store_output(validated, raw_path)

        logger.info(f"✅ Processing complete for {input_path.name}. Output: {output_path}")
        return {"file": str(input_path), "status": "success", "output": str(output_path)}

    except Exception as e:
        logger.exception(f"❌ Error processing {input_path}: {e}")
        return {"file": str(input_path), "status": "failed", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Intelligent Insurance Claim Processing System")
    parser.add_argument("--input", required=True, help="Path to a file or folder of claim documents")
    args = parser.parse_args()

    input_path = Path(args.input)

    if not input_path.exists():
        logger.error(f"❌ Input path not found: {input_path}")
        return

    results = []

    # If a folder is provided → batch processing
    if input_path.is_dir():
        logger.info(f"📂 Detected folder input: {input_path}")
        claim_files = [
            f for f in input_path.glob("*") if f.suffix.lower() in SUPPORTED_EXTS
        ]

        if not claim_files:
            logger.warning(f"⚠️ No supported claim files found in {input_path}")
            return

        logger.info(f"🔍 Found {len(claim_files)} claim files to process.")
        for f in claim_files:
            results.append(process_single_file(f))

    # If a single file is provided
    else:
        results.append(process_single_file(input_path))

    # Summary logging
    success = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]

    print("\n================= 📋 Processing Summary =================")
    print(f"✅ Successful: {len(success)}")
    print(f"❌ Failed: {len(failed)}")
    print("---------------------------------------------------------")
    for r in results:
        status_icon = "✅" if r["status"] == "success" else "❌"
        print(f"{status_icon} {r['file']}")
    print("=========================================================\n")

    # Save summary to JSON
    summary_path = DATA_DIR / "processed" / "summary.json"
    os.makedirs(summary_path.parent, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    logger.info(f"📊 Summary saved to: {summary_path}")

    print(f"📊 Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
