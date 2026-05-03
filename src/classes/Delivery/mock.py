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

SHIPMENT_STATUSES: List[str] = ["Neodoslaná", "Odoslaná", "V preprave", "Doručená", "Nedoručená", "Problém"]
LEGACY_SHIPMENT_STATUS_MAP: Dict[str, str] = {
    "NotSent": "Neodoslaná",
    "Sent": "Odoslaná",
    "InTransit": "V preprave",
    "Delivered": "Doručená",
    "NotDelivered": "Nedoručená",
    "Problem": "Problém",
}
SHIPMENT_STATUS_TRANSITIONS: Dict[str, List[str]] = {
    "Neodoslaná": ["Odoslaná", "Problém"],
    "Odoslaná": ["V preprave", "Nedoručená", "Problém"],
    "V preprave": ["Doručená", "Nedoručená", "Problém"],
    "Doručená": [],
    "Nedoručená": [],
    "Problém": ["Odoslaná", "V preprave", "Nedoručená"],
}
EXPRESS_SURCHARGE_EUR = 5.00
FREE_SHIPPING_THRESHOLD_EUR = 60.00

SHIPMENTS: Dict[int, dict] = {}
_ids = count(start=1)

def list_options() -> dict:
    return {"carriers": CARRIERS, "statuses": SHIPMENT_STATUSES}

def normalize_status(status: Optional[str]) -> str:
    raw = str(status or "").strip()
    if raw in SHIPMENT_STATUSES:
        return raw
    return LEGACY_SHIPMENT_STATUS_MAP.get(raw, raw or "Neodoslaná")

def _reachable_statuses(start: str) -> List[str]:
    seen = set()
    ordered: List[str] = []

    def visit(node: str):
        for nxt in SHIPMENT_STATUS_TRANSITIONS.get(node, []):
            if nxt == start or nxt in seen:
                continue
            seen.add(nxt)
            ordered.append(nxt)
            visit(nxt)

    visit(start)
    return [status for status in SHIPMENT_STATUSES if status in seen]

def allowed_next_statuses(status: Optional[str]) -> List[str]:
    current = normalize_status(status)
    return _reachable_statuses(current)

def _normalize_shipment_record(shipment: Optional[dict]) -> Optional[dict]:
    if shipment is None:
        return None
    shipment["status"] = normalize_status(shipment.get("status"))
    return shipment

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

def _resolve_delivery_terms(carrier: dict, delivery_type: str, order_base_price=None) -> dict:
    dtype = (delivery_type or "Standard").strip() or "Standard"
    try:
        base_order_price = float(order_base_price)
    except (TypeError, ValueError):
        base_order_price = None
    price = 0.0 if base_order_price is not None and base_order_price >= FREE_SHIPPING_THRESHOLD_EUR else float(carrier["price"])
    days = int(carrier["estimatedDays"])
    if dtype.lower() == "express":
        return {
            "deliveryType": "Express",
            "price": round(price + EXPRESS_SURCHARGE_EUR, 2),
            "estimatedDays": max(1, days - 1) if days > 1 else 1,
        }
    return {
        "deliveryType": "Standard",
        "price": price,
        "estimatedDays": days,
    }

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
    delivery = _resolve_delivery_terms(
        carrier,
        data.get("deliveryType") or "Standard",
        data.get("orderBasePrice"),
    )
    if data.get("priceOverride") is not None:
        delivery["price"] = round(float(data.get("priceOverride")), 2)
    if data.get("estimatedDaysOverride") is not None:
        delivery["estimatedDays"] = int(data.get("estimatedDaysOverride"))
    shipment = {
        "id": sid,
        "orderId": data.get("orderId"),
        "carrier": carrier["id"],
        "deliveryType": delivery["deliveryType"],
        "price": delivery["price"],
        "estimatedDays": delivery["estimatedDays"],
        "trackingNumber": tracking,
        "status": "Neodoslaná",
        "address": address,
        "sentAt": None,
        "trackingUrl": f"https://track.example/{tracking}",
    }
    SHIPMENTS[sid] = shipment
    return _normalize_shipment_record(shipment)

def update_shipment_status(shipment_id: int, status: str) -> Optional[dict]:
    shipment = SHIPMENTS.get(shipment_id)
    if shipment is None:
        return None
    shipment = _normalize_shipment_record(shipment)
    target = normalize_status(status)
    if target not in SHIPMENT_STATUSES:
        return {"error": f"Unknown status {status!r}", "allowed": SHIPMENT_STATUSES}
    current = shipment.get("status")
    if target != current and target not in allowed_next_statuses(current):
        return {
            "error": "invalid_status_transition",
            "message": f"Cannot change shipment status from {current!r} to {target!r}.",
            "allowedNext": allowed_next_statuses(current),
        }
    shipment["status"] = target
    if target == "Odoslaná" and not shipment["sentAt"]:
        shipment["sentAt"] = datetime.utcnow().isoformat()
    return shipment

def get_shipment_by_order_id(order_id: int) -> Optional[dict]:
    for shipment in SHIPMENTS.values():
        if shipment.get("orderId") == order_id:
            return _normalize_shipment_record(shipment)
    return None
