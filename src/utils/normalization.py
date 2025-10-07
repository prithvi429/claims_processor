import re
from datetime import datetime
from ..utils.logging import logger

def normalize_date(date_str):
    """Normalize date string to ISO format (basic regex fallback)."""
    if not date_str:
        return ""
    # Common patterns: MM/DD/YYYY, DD/MM/YYYY, words like "Oct 15, 2023"
    patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
        r'(\w{3})\s+(\d{1,2}),\s+(\d{4})'  # e.g., Oct 15, 2023
    ]
    for pattern in patterns:
        match = re.search(pattern, date_str, re.IGNORECASE)
        if match:
            try:
                if len(match.groups()) == 3:
                   