from __future__ import annotations

from typing import Optional

from ..classes.OrderManagment import mock as order_mock
from ..utils.validation import ensure_in


def list_options() -> dict:
    return order_mock.PAYMENT_TYPES


def validate(payment_type: Optional[str]) -> Optional[dict]:
    return ensure_in(payment_type, order_mock.PAYMENT_TYPES.keys(), "paymentType")


def surcharge_for(payment_type: Optional[str]) -> float:
    cfg = order_mock.PAYMENT_TYPES.get(payment_type) or {}
    return float(cfg.get("surcharge", 0.0))
