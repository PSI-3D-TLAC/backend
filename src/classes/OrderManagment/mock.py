"""Minimal mock orders: in-memory dict + simple status transitions.

Adds simple delivery method and payment type configuration that affect the
final order price and estimated delivery time.
"""
from __future__ import annotations

from datetime import datetime
from itertools import count
from typing import Dict, List, Optional


# Simplified, user-facing order lifecycle (issue requirement).
ORDER_STATUSES: List[str] = [
    "Created", "Paid", "Printing", "Shipped", "Delivered", "Cancelled",
]

# ---------------------------------------------------------------- delivery
# Each delivery method affects:
#   - price (added to the order total)
#   - estimatedDeliveryDays (added to the customer-visible ETA)
DELIVERY_METHODS: Dict[str, dict] = {
    "pickup":  {"label": "Personal pickup",  "price": 0.00, "estimatedDeliveryDays": 0},
    "courier": {"label": "Courier (standard)", "price": 4.50, "estimatedDeliveryDays": 3},
    "express": {"label": "Express courier",  "price": 9.90, "estimatedDeliveryDays": 1},
}

# ---------------------------------------------------------------- payment
# Each payment type may add a small surcharge (e.g. cash on delivery).
PAYMENT_TYPES: Dict[str, dict] = {
    "card":             {"label": "Card",             "surcharge": 0.00},
    "online":           {"label": "Online payment",   "surcharge": 0.00},
    "cash_on_delivery": {"label": "Cash on delivery", "surcharge": 1.50},
}


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
        "deliveryMethod": "courier",
        "deliveryPrice": 4.50,
        "estimatedDeliveryDays": 3,
        "paymentType": "card",
        "paymentSurcharge": 0.00,
        "totalPrice": 34.30,
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
        "deliveryMethod": "pickup",
        "deliveryPrice": 0.00,
        "estimatedDeliveryDays": 0,
        "paymentType": "online",
        "paymentSurcharge": 0.00,
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
        "deliveryMethod": "express",
        "deliveryPrice": 9.90,
        "estimatedDeliveryDays": 1,
        "paymentType": "cash_on_delivery",
        "paymentSurcharge": 1.50,
        "totalPrice": 53.40,
        "status": "Printing",
        "createdAt": datetime.utcnow().isoformat(),
    },
}


def _estimate(items: List[dict]) -> dict:
    qty = sum(int(it.get("quantity", 1)) for it in items)
    volume = 60.0 * qty
    time_min = 45 * qty
    base_price = round(volume * 0.12 + 5.0, 2)
    return {
        "estimatedVolumeCm3": volume,
        "estimatedTimeMin": time_min,
        "basePrice": base_price,
        "feasible": True,
    }


def _resolve_delivery(method: Optional[str]) -> dict:
    """Return the delivery config; falls back to ``courier`` if invalid/missing."""
    if not method or method not in DELIVERY_METHODS:
        method = "courier"
    cfg = DELIVERY_METHODS[method]
    return {
        "deliveryMethod": method,
        "deliveryPrice": float(cfg["price"]),
        "estimatedDeliveryDays": int(cfg["estimatedDeliveryDays"]),
    }


def _resolve_payment(payment: Optional[str]) -> dict:
    """Return the payment config; falls back to ``card`` if invalid/missing."""
    if not payment or payment not in PAYMENT_TYPES:
        payment = "card"
    cfg = PAYMENT_TYPES[payment]
    return {
        "paymentType": payment,
        "paymentSurcharge": float(cfg["surcharge"]),
    }


def list_options() -> dict:
    """Expose delivery methods and payment types for the frontend."""
    return {
        "deliveryMethods": [
            {"id": k, "label": v["label"], "price": v["price"], "estimatedDeliveryDays": v["estimatedDeliveryDays"]}
            for k, v in DELIVERY_METHODS.items()
        ],
        "paymentTypes": [
            {"id": k, "label": v["label"], "surcharge": v["surcharge"]}
            for k, v in PAYMENT_TYPES.items()
        ],
        "statuses": ORDER_STATUSES,
    }


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
    delivery = _resolve_delivery(data.get("deliveryMethod"))
    payment = _resolve_payment(data.get("paymentType"))
    total = round(
        estimate["basePrice"] + delivery["deliveryPrice"] + payment["paymentSurcharge"],
        2,
    )
    order = {
        "id": oid,
        "customerId": int(data.get("customerId", 1)),
        "items": items,
        "estimatedVolumeCm3": estimate["estimatedVolumeCm3"],
        "estimatedTimeMin": estimate["estimatedTimeMin"],
        "feasible": estimate["feasible"],
        "totalPrice": total,
        "status": "Created",
        "createdAt": datetime.utcnow().isoformat(),
        **delivery,
        **payment,
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
