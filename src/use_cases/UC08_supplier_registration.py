from __future__ import annotations

from typing import Optional

from ..classes.SupplierIntegration import mock as supplier_mock

def list_suppliers() -> list:
    return supplier_mock.list_suppliers()

def get_supplier(supplier_id: int) -> Optional[dict]:
    return supplier_mock.get_supplier(supplier_id)

def register_supplier(data: dict) -> dict:
    return supplier_mock.register_supplier_full(data)

def import_products(supplier_id: int, link: str) -> dict:
    return supplier_mock.import_supplier_products(supplier_id, link)
