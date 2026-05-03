from __future__ import annotations

from typing import Iterable, Optional

def ensure_in(value, allowed: Iterable, field_name: str) -> Optional[dict]:
    allowed_list = list(allowed)
    if value is None or value in allowed_list:
        return None
    return {
        "error": f"Unknown {field_name} {value!r}",
        "allowed": allowed_list,
    }

def require_fields(data: dict, fields: Iterable[str]) -> Optional[dict]:
    missing = [f for f in fields if not data.get(f)]
    if missing:
        return {"error": "missing_fields", "fields": missing}
    return None
