from __future__ import annotations

from typing import Optional

from ..classes.Catalog import mock as catalog_mock

def list_products(active_only: bool = False) -> list:
    return catalog_mock.list_products(active_only=active_only)

def get_product(product_id: int) -> Optional[dict]:
    return catalog_mock.get_product(product_id)

def create_product(data: dict) -> dict:
    return catalog_mock.create_product(data)

def update_product(product_id: int, data: dict) -> Optional[dict]:
    return catalog_mock.update_product(product_id, data)

def delete_product(product_id: int) -> bool:
    return catalog_mock.delete_product(product_id)
