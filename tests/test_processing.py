import pytest
from src.processing.nlp import extract_entities
from src.processing.genai import process_with_genai
from tests.conftest import sample_extracted, mock_openai

def test_extract_entities(sample_extracted):
    """Test spaCy NER on sample text."""
    text = sample_extracted["unstructured"]
    entities = extract_entities(text)
    assert isinstance(entities, dict)
    assert "DATE" in entities or "MONEY" in entities  # spaCy should detect dates/money
    # Specific: "Oct 15, 2023" should be DATE
    assert any("2023" in str(v) for v in entities.values())

def test_process_with_genai(sample_extracted, mock_openai, mocker):
    """Test GenAI processing (with mocked OpenAI)."""
    # Mock normalization utils if needed
    mocker.patch('src.utils.normalization.normalize_date', return_value="2023-10-15")
    mocker.patch('src.utils.normalization.normalize_amount', return_value=2500.0)
    
    processed = process_with_genai(sample_extracted)
    assert "claim_id" in processed
    assert processed["claim_id"] == "ABC123"
    assert processed["incident_date"] == "2023-10-15"
    assert processed["claim_amount"] == 2500.0
    assert "summary" in processed
    assert processed["confidence"] == 0.9  # From mock response

def test_process_with_genai_no_key(sample_extracted, mocker):
    """Test fallback without OpenAI key."""
    mocker.patch('src.config.OPENAI_API_KEY', None)
    processed = process_with_genai(sample_extracted)
    assert processed["summary"] == ""  # No GenAI
    assert processed["confidence"] == 0.95  # From extracted

def test_process_with_genai_error(sample_extracted, mock_openai, mocker):
    """Test error handling in GenAI."""
    mock_openai.side_effect = Exception("API error")
    processed = process_with_genai(sample_extracted)
    assert processed["claim_amount"] > 0  # Fallback normalization works