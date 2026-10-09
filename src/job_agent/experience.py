import re
from typing import Optional

_PATTERNS = (
    re.compile(r"(\d{1,2})\s*\+\s*years?\s+(?:of\s+)?experience", re.I),
    re.compile(r"(?:at least|minimum of|min\.?)\s*(\d{1,2})\s*years?", re.I),
    re.compile(r"(\d{1,2})\s*(?:-|to)\s*\d{1,2}\s*years?\s+(?:of\s+)?experience", re.I),
    re.compile(r"(\d{1,2})\s*years?\s+(?:of\s+)?experience", re.I),
)

def extract_experience_years(text: str) -> Optional[int]:
    """Return an explicitly stated numeric experience hint, or None."""
    text = text or ""
    for pattern in _PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                pass
    return None
