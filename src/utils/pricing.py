from __future__ import annotations

from typing import Iterable


def estimate_volume_cm3(items: Iterable[dict], per_item_cm3: float = 60.0) -> float:
    qty = sum(int(it.get("quantity", 1)) for it in items)
    return per_item_cm3 * qty


def estimate_print_time_min(items: Iterable[dict], per_item_min: int = 45) -> int:
    qty = sum(int(it.get("quantity", 1)) for it in items)
    return per_item_min * qty


def base_price_from_volume(volume_cm3: float, rate: float = 0.12, fixed: float = 5.0) -> float:
    return round(volume_cm3 * rate + fixed, 2)


def total_order_price(base_price: float, delivery_price: float, payment_surcharge: float) -> float:
    return round(float(base_price) + float(delivery_price) + float(payment_surcharge), 2)
