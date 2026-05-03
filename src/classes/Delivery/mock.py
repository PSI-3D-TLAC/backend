"""Minimal mock delivery: carriers, delivery options and shipments."""
from __future__ import annotations

from datetime import datetime
from itertools import count
from typing import Dict, List, Optional

CARRIERS: List[dict] = [
    {"id": 1, "name": "SlovakPost"},
    {"id": 2, "name": "PacketExpress"},
    {"id": 3, "name": "GLS"},
]

DELIVERY_OPTIONS: List[dict] = [
    {"id": 1, "carrierId": 1, "type": "Standard", "price": 3.50, "estimatedDays": 4},
    {"id": 2, "carrierId": 1, "type": "Express",  "price": 6.90, "estimatedDays": 2},
    {"id": 3, "carrierId": 2, "type": "Pickup",   "price": 2.50, "estimatedDays": 3},
    {"id": 4, "carrierId": 3, "type": "Express",  "price": 7.50, "estimatedDays": 1},
]

FREE_DELIVERY_THRESHOLD: float = 50.0

SHIPMENT_STATUSES: List[str] = ["NotSent", "Sent", "InTransit", "Delivered", "NotDelivered", "Problem"]

SHIPMENTS: Dict[int, dict] = {}
_ids = count(start=1)


def list_options() -> dict:
    return {
        "carriers": CARRIERS,
        "options": DELIVERY_OPTIONS,
        "freeDeliveryThreshold": FREE_DELIVERY_THRESHOLD,
    }


def _option(opt_id: int) -> Optional[dict]:
    return next((o for o in DELIVERY_OPTIONS if o["id"] == opt_id), None)


def create_shipment(data: dict) -> dict:
    sid = next(_ids)
    option = _option(int(data.get("deliveryOptionId", 0))) or DELIVERY_OPTIONS[0]
    order_total = float(data.get("orderTotal", 0.0))
    price = 0.0 if order_total >= FREE_DELIVERY_THRESHOLD else option["price"]
    tracking = f"TRK{sid:06d}"
    shipment = {
        "id": sid,
        "orderId": data.get("orderId"),
        "carrierId": option["carrierId"],
        "deliveryType": option["type"],
        "price": price,
        "trackingNumber": tracking,
        "status": "NotSent",
        "sentAt": None,
        "trackingUrl": f"https://track.example/{tracking}",
    }
    SHIPMENTS[sid] = shipment
    return shipment


def update_shipment_status(shipment_id: int, status: str) -> Optional[dict]:
    shipment = SHIPMENTS.get(shipment_id)
    if shipment is None:
        return None
    if status not in SHIPMENT_STATUSES:
        return {"error": f"Unknown status {status!r}", "allowed": SHIPMENT_STATUSES}
    shipment["status"] = status
    if status == "Sent" and not shipment["sentAt"]:
        shipment["sentAt"] = datetime.utcnow().isoformat()
    return shipment
