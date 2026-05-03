from __future__ import annotations

from typing import Optional

from ..classes.Support import mock as support_mock

def list_complaints(role: str, user_id: Optional[str]):
    role = (role or "").lower()
    if role in ("support", "admin"):
        return support_mock.list_complaints()
    if role == "customer":
        return support_mock.list_complaints(customer_id=user_id)
    return None

def get_complaint(complaint_id: int) -> Optional[dict]:
    return support_mock.get_complaint(complaint_id)

def update_complaint_status(complaint_id: int, status: str, comment: str, user: dict):
    return support_mock.update_complaint_status(
        complaint_id, status, comment=comment, user=user,
    )

def complaint_statuses() -> list:
    return list(support_mock.COMPLAINT_STATUSES)
