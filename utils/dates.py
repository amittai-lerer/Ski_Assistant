"""Date utilities."""

from datetime import date, timedelta
from typing import Dict, Any

def normalize_date_range(start_str: str, end_str: str) -> Dict[str, Any]:
    """Parse/normalize dates; if past or reversed, nudge to sane 7-day window."""
    try:
        start = date.fromisoformat(start_str)
        end = date.fromisoformat(end_str)
    except Exception as e:
        raise ValueError(f"Invalid date format (YYYY-MM-DD required): {e}")

    today = date.today()
    if start < today:
        start = today
    if end < start:
        end = start + timedelta(days=6)
    return {"start": start, "end": end}
