from __future__ import annotations

from typing import Optional

from ..classes.OrderManagment import mock as order_mock

def list_statuses() -> list:
    return list(order_mock.ORDER_STATUSES)

def list_orders(customer_id: Optional[int] = None) -> list:
    return order_mock.list_orders(customer_id=customer_id)

def get_order(order_id: int) -> Optional[dict]:
    return order_mock.get_order(order_id)

def update_status(order_id: int, status: str) -> Optional[dict]:
    return order_mock.update_status(order_id, status)

def describe(order: dict) -> str:
    if not order:
        return ""
    return f"Order #{order.get('id')} – {order.get('status', 'Unknown')}"
