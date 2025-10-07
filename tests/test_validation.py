import pytest
from src.validation.validator import validate_and_review, store_for_hitl
from tests.conftest import sample_extracted, in_memory_db
import json

def test_validate_high_confidence(sample_extracted):
    """Test auto-approval for high-confidence, valid data."""
    processed = sample_extracted.copy()
    processed["claim_amount"] = 5000.0  # Under limit
    processed["incident_date"] = "2023-10-15"
    processed["confidence"] = 0.95
    
    validated = validate_and_review(processed)
    assert validated["status"] == "ready_for_approval"

def test_validate_low_confidence(sample_extracted):
    """Test flagging for low confidence."""
    processed = sample_extracted.copy()
    processed["confidence"] = 0.7
    
    validated = validate_and_review(processed)
    assert validated["status"] == "review"

def test_validate_high_amount(sample_extracted):
    """Test rule violation: High amount."""
    processed = sample_extracted.copy()
    processed["claim_amount"] = 200000.0  # Over limit
    processed["confidence"] = 0.95
    
    validated = validate_and_review(processed)
    assert validated["status"] == "review"

def test_validate_missing_date(sample_extracted):
    """Test rule violation: Missing date."""
    processed = sample_extracted.copy()
    processed["incident_date"] = ""
    processed["confidence"] = 0.95
    
    validated = validate_and_review(processed)
    assert validated["status"] == "review"

def test_store_for_hitl(in_memory_db):
    """Test storing to DB (in-memory)."""
    processed = {"claim_id": "TEST123", "confidence": 0.7, "status": "review"}
    errors = ["Test error"]
    
    # Patch DATABASE_URL to use in-memory
    import src.config
    original_url = src.config.DATABASE_URL
    src.config.DATABASE_URL = "sqlite:///:memory:"
    
    try:
        store_for_hitl(processed, errors)
        
        # Query to verify
        cursor = in_memory_db.cursor()
        cursor.execute("SELECT * FROM claims WHERE claim_id=?", ("TEST123",))
        row = cursor.fetchone()
        assert row is not None
        assert json.loads(row[1])["claim_id"] == "TEST123"
        assert row[4] == "Test error"  # review_notes
    finally:
        src.config.DATABASE_URL = original_url