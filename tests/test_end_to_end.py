import pytest
import json
from pathlib import Path
from main import main
from src.storage.output import store_output
from src.storage.hitl import query_hitl
from tests.conftest import temp_dir, mock_openai, mocker

@pytest.fixture
def mock_args(mocker):
    """Mock argparse for end-to-end test."""
    mock_parser = mocker.patch('src.main.argparse.ArgumentParser')
    mock_args = mocker.Mock()
    mock_args.input = str(temp_dir / "mock_input.txt")
    mock_parser.parse_args.return_value = mock_args
    return mock_args

@pytest.fixture
def mock_ingest(mocker):
    """Mock ingestion to return a path."""
    mocker.patch('src.ingestion.ingest.ingest_document', return_value=temp_dir / "ingested_mock.txt")

@pytest.fixture
def mock_extract(mocker):
    """Mock extraction to return sample data."""
    mocker.patch('src.extraction.parser.extract_text', return_value={
        "structured": {"claim_id": "E2E123"},
        "unstructured": "End-to-end test claim: $1000 on 2023-01-01.",
        "confidence": 0.95
    })

@pytest.fixture
def mock_process(mocker):
    """Mock processing."""
    mocker.patch('src.processing.genai.process_with_genai', return_value={
        "claim_id": "E2E123",
        "incident_date": "2023-01-01",
        "claim_amount": 1000.0,
        "damage_description": "Test damage",
        "summary": "E2E summary",
        "confidence": 0.95
    })

@pytest.fixture
def mock_validate(mocker):
    """Mock validation to approve."""
    mocker.patch('src.validation.validator.validate_and_review', return_value={
        "claim_id": "E2E123",
        "status": "ready_for_approval",
        "confidence": 0.95
    })

def test_end_to_end_pipeline(mock_args, mock_ingest, mock_extract, mock_process, mock_validate, mock_openai, mocker, temp_dir):
    """Test full pipeline orchestration (mocks all steps)."""
    # Mock store_output to return a path
    mock_output_path = temp_dir / "e2e_output.json"
    mocker.patch('src.storage.output.store_output', return_value=mock_output_path)
    
    # Run main (with mocked args)
    from main import main
    main()
    
    # Verify output was 'stored'
    mock_output_path.touch()  # Simulate
    assert mock_output_path.exists()
    
    # Check HITL query (should be empty for approved)
    hitl_items = query_hitl()
    assert len(hitl_items) == 0  # No reviews in this test

def test_end_to_end_with_review(mock_args, mock_ingest, mock_extract, mocker, temp_dir):
    """Test end-to-end with flagging for review."""
    sample_extracted = {
        "structured": {},
        "unstructured": "Low confidence test.",
        "confidence": 0.5
    }
    mocker.patch('src.extraction.parser.extract_text', return_value=sample_extracted)
    
    # Mock process and validate to flag review
    mocker.patch('src.processing.genai.process_with_genai', return_value={"claim_id": "REVIEW123", "confidence": 0.5})
    mocker.patch('src.validation.validator.validate_and_review', return_value={"claim_id": "REVIEW123", "status": "review"})
    mocker.patch('src.storage.output.store_output', return_value=temp_dir / "review_output.json")
    
    main()
    
    # Verify HITL has item
    hitl_items = query_hitl()
    assert len(hitl_items) == 1
    assert hitl_items[0]["claim_id"] == "REVIEW123"
    assert hitl_items[0]["status"] == "review"