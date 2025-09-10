"""Error handling utilities."""

from typing import Dict, Any

def _ok(payload: Dict[str, Any], **extras) -> Dict[str, Any]:
    """Standard success envelope."""
    out = {"ok": True, **payload}
    out.update(extras)
    return out

def _err(code: str, message: str, **extras) -> Dict[str, Any]:
    """Standard error envelope."""
    out = {"ok": False, "error": code, "message": message}
    out.update(extras)
    return out
