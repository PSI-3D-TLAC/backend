from __future__ import annotations

from typing import Optional

from ..classes.OrderManagment import mock as order_mock
from ..utils.pricing import (
    base_price_from_volume,
    estimate_print_time_min,
    estimate_volume_cm3,
)
from ..utils.validation import ensure_in

def estimate(items: list) -> dict:
    volume = estimate_volume_cm3(items)
    return {
        "estimatedVolumeCm3": volume,
        "estimatedTimeMin": estimate_print_time_min(items),
        "basePrice": base_price_from_volume(volume),
        "feasible": True,
    }

def validate(data: dict) -> Optional[dict]:
    err = ensure_in(
        data.get("deliveryMethod"),
        order_mock.DELIVERY_METHODS.keys(),
        "deliveryMethod",
    )
    if err:
        return err
    return ensure_in(
        data.get("paymentType"),
        order_mock.PAYMENT_TYPES.keys(),
        "paymentType",
    )

def create(data: dict) -> dict:
    return order_mock.create_order(data)
