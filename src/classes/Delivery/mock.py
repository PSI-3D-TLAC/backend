from __future__ import annotations

from datetime import datetime
from itertools import count
from typing import Dict, List, Optional

CARRIERS: List[dict] = [
    {"id": "GLS", "name": "GLS", "price": 4.90, "estimatedDays": 2},
    {"id": "Slovenská pošta", "name": "Slovenská pošta", "price": 3.50, "estimatedDays": 4},
    {"id": "DHL", "name": "DHL", "price": 7.90, "estimatedDays": 1},
]

ALLOWED_CARRIERS: List[str] = [c["id"] for c in CARRIERS]

REQUIRED_ADDRESS_FIELDS: List[str] = [
    "fullName", "street", "city", "postalCode", "country", "phone",
]

SHIPMENT_STATUSES: List[str] = ["NotSent", "Sent", "InTransit", "Delivered", "NotDelivered", "Problem"]

SHIPMENTS: Dict[int, dict] = {}
_ids = count(start=1)


def list_options() -> dict:
    return {"carriers": CARRIERS}


def _carrier(carrier_id: str) -> Optional[dict]:
    return next((c for c in CARRIERS if c["id"] == carrier_id), None)


def _validate_address(address) -> Optional[dict]:
    if not isinstance(address, dict):
        return {"error": "address_required", "message": "Delivery address is required.",
                "missing": REQUIRED_ADDRESS_FIELDS}
    missing = [f for f in REQUIRED_ADDRESS_FIELDS
               if not str(address.get(f, "")).strip()]
    if missing:
        return {"error": "address_incomplete",
                "message": f"Missing address fields: {', '.join(missing)}",
                "missing": missing}
    return None


def create_shipment(data: dict):
    carrier_id = (data.get("carrier") or "").strip()
    carrier = _carrier(carrier_id)
    if carrier is None:
        return {"error": "unknown_carrier",
                "message": f"Unknown carrier {carrier_id!r}",
                "allowed": ALLOWED_CARRIERS}
    addr_err = _validate_address(data.get("address"))
    if addr_err is not None:
        return addr_err
    address = {f: str(data["address"][f]).strip() for f in REQUIRED_ADDRESS_FIELDS}
    sid = next(_ids)
    tracking = f"{carrier['id'][:3].upper()}{sid:08d}"
    shipment = {
        "id": sid,
        "orderId": data.get("orderId"),
        "carrier": carrier["id"],
        "deliveryType": (data.get("deliveryType") or "Standard").strip() or "Standard",
        "price": carrier["price"],
        "estimatedDays": carrier["estimatedDays"],
        "trackingNumber": tracking,
        "status": "NotSent",
        "address": address,
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
