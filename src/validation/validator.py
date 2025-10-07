"""Simple validation rules and HITL flagging."""

def validate_claim(claim: dict) -> dict:
    # Simple checks
    issues = []
    if not claim.get('claim_id'):
        issues.append('missing_claim_id')
    return {'valid': len(issues) == 0, 'issues': issues}
