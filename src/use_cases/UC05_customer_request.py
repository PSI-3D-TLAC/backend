from __future__ import annotations

from typing import Optional

from ..classes.OrderManagment import mock as order_mock
from ..classes.Support import mock as support_mock

def list_requests(role: str, user_id: Optional[str]):
    role = (role or "").lower()
    if role in ("support", "admin"):
        return support_mock.list_requests()
    if role == "customer":
        return support_mock.list_requests(customer_id=user_id)
    return None

def get_request(request_id: int) -> Optional[dict]:
    return support_mock.get_request(request_id)

def update_request_status(request_id: int, status: str, comment: str, user: dict):
    return support_mock.update_request_status(
        request_id, status, comment=comment, user=user,
    )

def request_statuses() -> list:
    return list(support_mock.REQUEST_STATUSES)

def dashboard(role: str, user_id: Optional[str]) -> dict:
    from . import UC09_complaint_handling
    payload = {
        "requests": list_requests(role, user_id) or [],
        "complaints": UC09_complaint_handling.list_complaints(role, user_id) or [],
        "requestStatuses": request_statuses(),
        "complaintStatuses": UC09_complaint_handling.complaint_statuses(),
    }
    if (role or "").lower() in ("support", "admin"):
        payload["orders"] = order_mock.list_orders()
    return payload
