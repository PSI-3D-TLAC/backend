\
\
\
\
\
from __future__ import annotations

from datetime import datetime
from itertools import count
from typing import Dict, List, Optional

from ..Catalog import mock as catalog_mock
                                                              
ORDER_STATUSES: List[str] = [
    "Prijatá",
    "Zaplatená",
    "Prevzatá na spracovanie",
    "Rezervovaná tlačiareň",
    "Tlačí sa",
    "Balenie",
    "Pripravená na odoslanie",
    "Odoslaná",
    "Doručená",
    "Čaká na údaje od zákazníka",
    "Pozastavená",
    "Zrušená",
]

LEGACY_ORDER_STATUS_MAP: Dict[str, str] = {
    "Created": "Prijatá",
    "Paid": "Zaplatená",
    "Printing": "Tlačí sa",
    "Shipped": "Odoslaná",
    "Delivered": "Doručená",
    "Cancelled": "Zrušená",
}

ORDER_STATUS_TRANSITIONS: Dict[str, List[str]] = {
    "Prijatá": ["Zaplatená", "Čaká na údaje od zákazníka", "Zrušená"],
    "Zaplatená": ["Prevzatá na spracovanie", "Čaká na údaje od zákazníka", "Pozastavená", "Zrušená"],
    "Prevzatá na spracovanie": ["Rezervovaná tlačiareň", "Čaká na údaje od zákazníka", "Pozastavená", "Zrušená"],
    "Rezervovaná tlačiareň": ["Tlačí sa", "Pozastavená", "Zrušená"],
    "Tlačí sa": ["Balenie", "Pozastavená"],
    "Balenie": ["Pripravená na odoslanie", "Pozastavená"],
    "Pripravená na odoslanie": ["Odoslaná"],
    "Odoslaná": ["Doručená"],
    "Doručená": [],
    "Čaká na údaje od zákazníka": ["Prijatá", "Zaplatená", "Prevzatá na spracovanie", "Zrušená"],
    "Pozastavená": ["Prevzatá na spracovanie", "Rezervovaná tlačiareň", "Zrušená"],
    "Zrušená": [],
}

MAIN_ORDER_FLOW: List[str] = [
    "Prijatá",
    "Zaplatená",
    "Prevzatá na spracovanie",
    "Rezervovaná tlačiareň",
    "Tlačí sa",
    "Balenie",
    "Pripravená na odoslanie",
    "Odoslaná",
    "Doručená",
]

                               

from ..Delivery.mock import CARRIERS as _CARRIERS

DELIVERY_METHODS: Dict[str, dict] = {
    c["id"]: {"label": c["name"], "price": float(c["price"]), "estimatedDeliveryDays": int(c["estimatedDays"])}
    for c in _CARRIERS
}

_DEFAULT_DELIVERY = next(iter(DELIVERY_METHODS))

                                                                      
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
        "deliveryMethod": "GLS",
        "deliveryPrice": 4.90,
        "estimatedDeliveryDays": 2,
        "paymentType": "card",
        "paymentSurcharge": 0.00,
        "totalPrice": 34.30,
        "status": "Prijatá",
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
        "deliveryMethod": "Slovenská pošta",
        "deliveryPrice": 3.50,
        "estimatedDeliveryDays": 4,
        "paymentType": "online",
        "paymentSurcharge": 0.00,
        "totalPrice": 18.50,
        "status": "Zaplatená",
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
        "deliveryMethod": "DHL",
        "deliveryPrice": 7.90,
        "estimatedDeliveryDays": 1,
        "paymentType": "cash_on_delivery",
        "paymentSurcharge": 1.50,
        "totalPrice": 53.40,
        "status": "Tlačí sa",
        "createdAt": datetime.utcnow().isoformat(),
    },
}

QUALITY_MULTIPLIERS: Dict[str, dict] = {
    "low": {"price": 0.8, "time": 0.7},
    "medium": {"price": 1.0, "time": 1.0},
    "standard": {"price": 1.0, "time": 1.0},
    "high": {"price": 1.4, "time": 1.6},
}

ORDER_SETUP_FEE_EUR = 1.50
FALLBACK_PRODUCT_PRICE_EUR = 10.00
BASE_ITEM_TIME_MIN = 45
DEFAULT_DELIVERY_ADDRESS: Dict[str, str] = {
    "fullName": "Demo Customer",
    "street": "Main Street 1",
    "city": "Bratislava",
    "postalCode": "81101",
    "country": "Slovakia",
    "phone": "+421900000000",
}

def normalize_status(status: Optional[str]) -> str:
    raw = str(status or "").strip()
    if raw in ORDER_STATUSES:
        return raw
    return LEGACY_ORDER_STATUS_MAP.get(raw, raw or "Prijatá")

def _reachable_statuses(start: str) -> List[str]:
    seen = set()
    ordered: List[str] = []

    def visit(node: str):
        for nxt in ORDER_STATUS_TRANSITIONS.get(node, []):
            if nxt == start or nxt in seen:
                continue
            seen.add(nxt)
            ordered.append(nxt)
            visit(nxt)

    visit(start)
    return [status for status in ORDER_STATUSES if status in seen]

def allowed_next_statuses(status: Optional[str]) -> List[str]:
    current = normalize_status(status)
    reachable = _reachable_statuses(current)
    if current not in MAIN_ORDER_FLOW:
        return reachable
    current_index = MAIN_ORDER_FLOW.index(current)
    return [
        candidate for candidate in reachable
        if candidate not in MAIN_ORDER_FLOW or MAIN_ORDER_FLOW.index(candidate) >= current_index
    ]

def _normalize_order_record(order: Optional[dict]) -> Optional[dict]:
    if order is None:
        return None
    order["status"] = normalize_status(order.get("status"))
    if not str(order.get("deliveryType") or "").strip():
        order["deliveryType"] = "Standard"
    if not isinstance(order.get("deliveryAddress"), dict):
        order["deliveryAddress"] = dict(DEFAULT_DELIVERY_ADDRESS)
    return order

def _quality_key(value) -> str:
    key = str(value or "").strip().lower()
    if key in QUALITY_MULTIPLIERS:
        return key
    return "medium"

def _estimate(items: List[dict]) -> dict:
    volume = 0.0
    time_total = 0.0
    price_total = 0.0
    has_items = False

    for item in items:
        try:
            qty = int(item.get("quantity", 1))
        except (TypeError, ValueError):
            qty = 1
        qty = max(1, min(100, qty))
        has_items = True

        product = catalog_mock.get_product(item.get("productId"))
        try:
            product_price = float(product.get("price")) if product is not None else FALLBACK_PRODUCT_PRICE_EUR
        except (TypeError, ValueError, AttributeError):
            product_price = FALLBACK_PRODUCT_PRICE_EUR

        quality = QUALITY_MULTIPLIERS[_quality_key(item.get("precision"))]
        volume += 60.0 * qty
        time_total += BASE_ITEM_TIME_MIN * qty * quality["time"]
        price_total += product_price * qty * quality["price"]

    base_price = round(price_total + (ORDER_SETUP_FEE_EUR if has_items else 0.0), 2)
    return {
        "estimatedVolumeCm3": volume,
        "estimatedTimeMin": int(round(time_total)),
        "basePrice": base_price,
        "feasible": True,
    }

EXPRESS_SURCHARGE_EUR = 5.00
FREE_SHIPPING_THRESHOLD_EUR = 60.00

def _resolve_delivery(method: Optional[str], delivery_type: Optional[str] = None, items_price: float = 0.0) -> dict:
    \
    if not method or method not in DELIVERY_METHODS:
        method = _DEFAULT_DELIVERY
    cfg = DELIVERY_METHODS[method]
    price = 0.0 if float(items_price) >= FREE_SHIPPING_THRESHOLD_EUR else float(cfg["price"])
    days = int(cfg["estimatedDeliveryDays"])
    dtype = (delivery_type or "Standard").strip() or "Standard"
    if dtype.lower() == "express":
        price = round(price + EXPRESS_SURCHARGE_EUR, 2)
        days = max(1, days - 1) if days > 1 else 1
        dtype = "Express"
    else:
        dtype = "Standard"
    return {
        "deliveryMethod": method,
        "deliveryType": dtype,
        "deliveryPrice": price,
        "estimatedDeliveryDays": days,
    }

def _resolve_payment(payment: Optional[str]) -> dict:
    \
    if not payment or payment not in PAYMENT_TYPES:
        payment = "card"
    cfg = PAYMENT_TYPES[payment]
    return {
        "paymentType": payment,
        "paymentSurcharge": float(cfg["surcharge"]),
    }

def list_options() -> dict:
    \
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
    items = [_normalize_order_record(o) for o in ORDERS.values()]
    if customer_id is not None:
        items = [o for o in items if o["customerId"] == customer_id]
    return items

def get_order(order_id: int) -> Optional[dict]:
    return _normalize_order_record(ORDERS.get(order_id))

def create_order(data: dict) -> dict:
    oid = next(_ids)
    items = data.get("items") or []

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
    dtype = data.get("deliveryType")
    if not dtype and isinstance(data.get("delivery"), dict):
        dtype = data["delivery"].get("deliveryType")
    delivery = _resolve_delivery(data.get("deliveryMethod"), dtype, estimate["basePrice"])
    payment = _resolve_payment(data.get("paymentType"))
    total = round(
        estimate["basePrice"] + delivery["deliveryPrice"] + payment["paymentSurcharge"],
        2,
    )
    delivery_request = data.get("delivery") if isinstance(data.get("delivery"), dict) else None
    delivery_address = None
    if isinstance(delivery_request, dict) and isinstance(delivery_request.get("address"), dict):
        delivery_address = {
            key: str(value).strip()
            for key, value in delivery_request["address"].items()
        }
    order = {
        "id": oid,
        "customerId": int(data.get("customerId", 1)),
        "items": items,
        "estimatedVolumeCm3": estimate["estimatedVolumeCm3"],
        "estimatedTimeMin": estimate["estimatedTimeMin"],
        "feasible": estimate["feasible"],
        "totalPrice": total,
        "status": "Prijatá",
        "createdAt": datetime.utcnow().isoformat(),
        "deliveryAddress": delivery_address,
        **delivery,
        **payment,
    }
    ORDERS[oid] = order
    return _normalize_order_record(order)

def update_status(order_id: int, status: str) -> Optional[dict]:
    order = ORDERS.get(order_id)
    if order is None:
        return None
    order = _normalize_order_record(order)
    target = normalize_status(status)
    if target not in ORDER_STATUSES:
        return {"error": f"Unknown status {status!r}", "allowed": ORDER_STATUSES}
    current = order.get("status")
    if target != current and target not in allowed_next_statuses(current):
        return {
            "error": "invalid_status_transition",
            "message": f"Cannot change order status from {current!r} to {target!r}.",
            "allowedNext": allowed_next_statuses(current),
        }
    order["status"] = target
    return order
