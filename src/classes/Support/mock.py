"""Minimal mock support module: customer requests and complaints."""
from __future__ import annotations

from datetime import datetime
from itertools import count
from typing import Dict, List

REQUESTS: Dict[int, dict] = {}
COMPLAINTS: Dict[int, dict] = {}

_req_ids = count(start=1)
_comp_ids = count(start=1)

COMPLAINT_REASONS: List[str] = ["damaged", "missing_parts", "full_return"]


def create_request(data: dict) -> dict:
    rid = next(_req_ids)
    record = {
        "id": rid,
        "orderId": data.get("orderId"),
        "type": data.get("type", "change"),  # change | cancel | other
        "description": data.get("description", ""),
        "status": "Open",
        "createdAt": datetime.utcnow().isoformat(),
    }
    REQUESTS[rid] = record
    return record


def list_requests() -> List[dict]:
    return list(REQUESTS.values())


def update_request_status(rid: int, status: str) -> dict | None:
    record = REQUESTS.get(rid)
    if record is None:
        return None
    record["status"] = status or "Resolved"
    return record


def create_complaint(data: dict) -> dict:
    cid = next(_comp_ids)
    reason = data.get("reason", "damaged")
    if reason not in COMPLAINT_REASONS:
        return {"error": f"Unknown reason {reason!r}", "allowed": COMPLAINT_REASONS}
    record = {
        "id": cid,
        "orderId": data.get("orderId"),
        "reason": reason,
        "description": data.get("description", ""),
        "status": "Created",
        "createdAt": datetime.utcnow().isoformat(),
    }
    COMPLAINTS[cid] = record
    return record


def list_complaints() -> List[dict]:
    return list(COMPLAINTS.values())
