import pytest
import os
from pathlib import Path
import tempfile
import sqlite3

# Global fixture: Temporary directory for test outputs
@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

# Global fixture: Mock sample extracted data (from mock_claim.txt)
@pytest.fixture
def sample_extracted():
    return {
        "structured": {
            "claim_id": "ABC123",
            "date": "10/15/2023",
            "amount": "$2,500"
        },
        "unstructured": """
        Claim ID: ABC123
        Date: 10/15/2023
        Amount: $2,500
        Description: Car accident on Oct 15, 2023. Damage to bumper due to rear-end collision. Estimated cost $2500.
        """,
        "confidence": 0.95
    }

# Global fixture: In-memory SQLite for DB tests
@pytest.fixture
def in_memory_db():
    conn = sqlite3.connect(':memory:')
    yield conn
    conn.close()

# Global fixture: Mock OpenAI client (for processing tests)
@pytest.fixture
def mock_openai(mocker):
    mock_client = mocker.patch('openai.OpenAI')
    mock_response = mocker.Mock()
    mock_choice = mocker.Mock()
    mock_choice.message.content = '{"claim_id": "ABC123", "incident_date": "2023-10-15", "claim_amount": 2500, "damage_description": "Car accident", "summary": "Summary test", "confidence": 0.9}'
    mock_response.choices = [mock_choice]
    mock_client.return_value.chat.completions.create.return_value = mock_response
    return mock_client