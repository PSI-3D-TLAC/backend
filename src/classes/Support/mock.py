\
\
\
\
\
\
from __future__ import annotations

from datetime import datetime
from itertools import count
from typing import Dict, List, Optional

REQUESTS: Dict[int, dict] = {}
COMPLAINTS: Dict[int, dict] = {}

_req_ids = count(start=1)
_comp_ids = count(start=1)

COMPLAINT_REASONS: List[str] = ["damaged", "missing_parts", "full_return"]

REQUEST_STATUSES: List[str] = [
    "New",
    "In Progress",
    "Waiting for Customer",
    "Resolved",
    "Closed",
]
COMPLAINT_STATUSES: List[str] = [
    "Submitted",
    "Under Review",
    "Approved",
    "Rejected",
    "Refund Issued",
    "Replacement Created",
    "Closed",
]

def _now() -> str:
    return datetime.utcnow().isoformat()

def _history_entry(prev: str, new: str, changed_by: str, comment: str) -> dict:
    return {
        "previousStatus": prev,
        "newStatus": new,
        "changedBy": changed_by,
        "comment": comment or "",
        "timestamp": _now(),
    }

                                                                           
def create_request(data: dict, user: Optional[dict] = None) -> dict:
    rid = next(_req_ids)
    user = user or {}
    customer_id = data.get("customerId") or user.get("id")
    record = {
        "id": rid,
        "customerId": customer_id,
        "orderId": data.get("orderId"),
        "type": data.get("type", "change"),                           
        "description": data.get("description", ""),
        "status": "New",
        "createdAt": _now(),
        "history": [
            _history_entry("", "New", str(user.get("id") or "customer"), "Request created.")
        ],
    }
    REQUESTS[rid] = record
    return record

def list_requests(customer_id: Optional[int] = None) -> List[dict]:
    items = list(REQUESTS.values())
    if customer_id is not None:
        items = [r for r in items if str(r.get("customerId")) == str(customer_id)]
    return items

def get_request(rid: int) -> Optional[dict]:
    return REQUESTS.get(rid)

def update_request_status(
    rid: int, status: str, comment: str = "", user: Optional[dict] = None
) -> dict | None:
    record = REQUESTS.get(rid)
    if record is None:
        return None
    if status not in REQUEST_STATUSES:
        return {"error": f"Unknown status {status!r}", "allowed": REQUEST_STATUSES}
    user = user or {}
    prev = record.get("status", "")
    changed_by = str(user.get("id") or user.get("role") or "support")
    record["status"] = status
    record.setdefault("history", []).append(
        _history_entry(prev, status, changed_by, comment)
    )
    return record

                                                                             
def create_complaint(data: dict, user: Optional[dict] = None) -> dict:
    cid = next(_comp_ids)
    reason = data.get("reason", "damaged")
    if reason not in COMPLAINT_REASONS:
        return {"error": f"Unknown reason {reason!r}", "allowed": COMPLAINT_REASONS}
    user = user or {}
    customer_id = data.get("customerId") or user.get("id")
    record = {
        "id": cid,
        "customerId": customer_id,
        "orderId": data.get("orderId"),
        "reason": reason,
        "description": data.get("description", ""),
        "status": "Submitted",
        "createdAt": _now(),
        "history": [
            _history_entry("", "Submitted", str(user.get("id") or "customer"), "Complaint submitted.")
        ],
    }
    COMPLAINTS[cid] = record
    return record

def list_complaints(customer_id: Optional[int] = None) -> List[dict]:
    items = list(COMPLAINTS.values())
    if customer_id is not None:
        items = [c for c in items if str(c.get("customerId")) == str(customer_id)]
    return items

def get_complaint(cid: int) -> Optional[dict]:
    return COMPLAINTS.get(cid)

def update_complaint_status(
    cid: int, status: str, comment: str = "", user: Optional[dict] = None
) -> dict | None:
    record = COMPLAINTS.get(cid)
    if record is None:
        return None
    if status not in COMPLAINT_STATUSES:
        return {"error": f"Unknown status {status!r}", "allowed": COMPLAINT_STATUSES}
    user = user or {}
    prev = record.get("status", "")
    changed_by = str(user.get("id") or user.get("role") or "support")
    record["status"] = status
    record.setdefault("history", []).append(
        _history_entry(prev, status, changed_by, comment)
    )
    return record
