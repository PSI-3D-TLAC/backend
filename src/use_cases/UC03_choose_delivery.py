from __future__ import annotations

from typing import Optional

from ..classes.OrderManagment import mock as order_mock
from ..utils.validation import ensure_in


def list_options() -> dict:
    return order_mock.DELIVERY_METHODS


def validate(method: Optional[str]) -> Optional[dict]:
    return ensure_in(method, order_mock.DELIVERY_METHODS.keys(), "deliveryMethod")


def price_for(method: Optional[str]) -> float:
    cfg = order_mock.DELIVERY_METHODS.get(method) or {}
    return float(cfg.get("price", 0.0))


def days_for(method: Optional[str]) -> int:
    cfg = order_mock.DELIVERY_METHODS.get(method) or {}
    return int(cfg.get("estimatedDeliveryDays", 0))
