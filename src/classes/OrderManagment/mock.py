"""Minimal mock orders: in-memory dict + simple status transitions."""
from __future__ import annotations

from datetime import datetime
from itertools import count
from typing import Dict, List, Optional


ORDER_STATUSES: List[str] = [
    "Created", "Evaluated", "WaitingForConfirmation", "Confirmed", "Paid",
    "Processing", "PrinterReserved", "Printing", "Packing", "ReadyForDelivery",
    "Shipped", "Delivered", "Cancelled", "Suspended",
]

_ids = count(start=4)

ORDERS: Dict[int, dict] = {
    1: {
        "id": 1,
        "customerId": 1,
        "items": [
            {"productId": 1, "modelRef": None, "materialId": 1, "precision": "standard", "split": False, "quantity": 2}
        ],
        "estimatedVolumeCm3": 120.0,
        "estimatedTimeMin": 90,
        "feasible": True,
        "totalPrice": 29.80,
        "status": "Created",
        "createdAt": datetime.utcnow().isoformat(),
    },
    2: {
        "id": 2,
        "customerId": 1,
        "items": [
            {"productId": 2, "modelRef": None, "materialId": 3, "precision": "high", "split": False, "quantity": 1}
        ],
        "estimatedVolumeCm3": 80.0,
        "estimatedTimeMin": 75,
        "feasible": True,
        "totalPrice": 18.50,
        "status": "Paid",
        "createdAt": datetime.utcnow().isoformat(),
    },
    3: {
        "id": 3,
        "customerId": 1,
        "items": [
            {"productId": 3, "modelRef": None, "materialId": 1, "precision": "standard", "split": True, "quantity": 4}
        ],
        "estimatedVolumeCm3": 200.0,
        "estimatedTimeMin": 180,
        "feasible": True,
        "totalPrice": 42.00,
        "status": "Printing",
        "createdAt": datetime.utcnow().isoformat(),
    },
}


def _estimate(items: List[dict]) -> dict:
    qty = sum(int(it.get("quantity", 1)) for it in items)
    volume = 60.0 * qty
    time_min = 45 * qty
    price = round(volume * 0.12 + 5.0, 2)
    return {"estimatedVolumeCm3": volume, "estimatedTimeMin": time_min, "totalPrice": price, "feasible": True}


def list_orders(customer_id: Optional[int] = None) -> List[dict]:
    items = list(ORDERS.values())
    if customer_id is not None:
        items = [o for o in items if o["customerId"] == customer_id]
    return items


def get_order(order_id: int) -> Optional[dict]:
    return ORDERS.get(order_id)


def create_order(data: dict) -> dict:
    oid = next(_ids)
    items = data.get("items") or []
    # Frontend may send a flat single-item body
    # ({productId, materialId, printQuality, quantity, customModelFileName}).
    if not items and ("productId" in data or "customModelFileName" in data):
        try:
            qty = int(data.get("quantity", 1))
        except (TypeError, ValueError):
            qty = 1
        qty = max(1, min(100, qty))
        items = [{
            "productId": data.get("productId"),
            "modelRef": data.get("customModelFileName"),
            "materialId": data.get("materialId"),
            "precision": data.get("printQuality", "medium"),
            "split": False,
            "quantity": qty,
        }]
    estimate = _estimate(items)
    order = {
        "id": oid,
        "customerId": int(data.get("customerId", 1)),
        "items": items,
        "status": "Created",
        "createdAt": datetime.utcnow().isoformat(),
        **estimate,
    }
    ORDERS[oid] = order
    return order


def update_status(order_id: int, status: str) -> Optional[dict]:
    order = ORDERS.get(order_id)
    if order is None:
        return None
    if status not in ORDER_STATUSES:
        return {"error": f"Unknown status {status!r}", "allowed": ORDER_STATUSES}
    order["status"] = status
    return order
