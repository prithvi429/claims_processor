"""
src/validation/validator.py
--------------------------------
Validates extracted and processed claim data.
Handles rule-based checks, confidence thresholds, and HITL (Human-in-the-Loop) fallback.
"""

from typing import Dict, Any, List
from src.config import CONFIDENCE_THRESHOLD, MAX_CLAIM_AMOUNT, MIN_CLAIM_AMOUNT
from src.utils.logging import logger


def validate_and_review(processed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate processed claim data using business rules.
    If validation fails or confidence is low, flag for human review.
    """
    errors: List[str] = []
    validated = processed.copy()

    logger.info("🧩 Running validation checks...")

    # Example checks — adapt to your real schema
    amount = validated.get("amount")
    confidence = validated.get("confidence", 1.0)

    # --- Check 1: Amount range ---
    try:
        if amount is not None:
            amount = float(amount)
            if amount > MAX_CLAIM_AMOUNT:
                errors.append(f"Amount exceeds limit ({amount} > {MAX_CLAIM_AMOUNT})")
            elif amount < MIN_CLAIM_AMOUNT:
                errors.append(f"Amount below minimum ({amount} < {MIN_CLAIM_AMOUNT})")
        else:
            errors.append("Missing claim amount")
    except Exception as e:
        errors.append(f"Invalid amount value: {e}")

    # --- Check 2: Confidence ---
    try:
        if confidence < CONFIDENCE_THRESHOLD:
            errors.append(f"Low model confidence: {confidence:.2f}")
    except Exception as e:
        errors.append(f"Invalid confidence value: {e}")

    # --- If errors, store for HITL ---
    if errors:
        logger.warning(f"⚠️ Validation failed for claim: {errors}")
        store_for_hitl(validated, errors)
    else:
        logger.info("✅ Validation passed successfully.")

    validated["validation_errors"] = errors
    return validated


# --------------------------------------------------------------------------
# HITL Storage Function (Safe for missing fields)
# --------------------------------------------------------------------------
def store_for_hitl(processed: dict, errors: list):
    """
    Store low-confidence or failed claims into HITL database for human review.
    Safe for missing fields.
    """
    from src.storage.hitl import insert_hitl_record

    claim_id = processed.get("claim_id", f"temp_{int(__import__('time').time())}")
    claim_amount = processed.get("amount", None)
    claim_date = processed.get("date", None)

    insert_hitl_record(
        claim_id,
        claim_amount,
        claim_date,
        errors,
    )

    logger.info(f"🗂️ Stored claim {claim_id} for human review with {len(errors)} errors.")
