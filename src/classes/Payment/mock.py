"""Minimal mock payment gateway. Use ``forceFail`` in the request to simulate failures."""
from __future__ import annotations

from datetime import datetime
from itertools import count
from typing import Dict, List

PAYMENTS: Dict[int, dict] = {}
_ids = count(start=1)

PAYMENT_METHODS: List[str] = ["card", "bank_transfer", "paypal", "apple_pay"]


def pay(data: dict) -> dict:
    pid = next(_ids)
    method = data.get("method", "card")
    amount = float(data.get("amount", 0.0))
    force_fail = bool(data.get("forceFail", False))
    if method not in PAYMENT_METHODS or amount <= 0 or force_fail:
        record = {
            "id": pid,
            "orderId": data.get("orderId"),
            "amount": amount,
            "method": method,
            "status": "FAILED",
            "reason": "Forced failure" if force_fail else "Invalid method or amount",
            "paidAt": None,
        }
        PAYMENTS[pid] = record
        return {"success": False, "payment": record}
    record = {
        "id": pid,
        "orderId": data.get("orderId"),
        "amount": amount,
        "method": method,
        "status": "SUCCESS",
        "reason": None,
        "paidAt": datetime.utcnow().isoformat(),
    }
    PAYMENTS[pid] = record
    return {"success": True, "payment": record}
