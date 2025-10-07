"""HITL hooks (placeholder for human-in-the-loop workflows)."""

def flag_for_review(claim: dict) -> None:
    # Append to a local file or DB in real usage
    with open('logs/hitl_flags.log', 'a', encoding='utf-8') as f:
        f.write(str(claim) + "\n")
