from src.validation import validator

def test_validator():
    result = validator.validate_claim({'claim_id': 'X'})
    assert result['valid']
