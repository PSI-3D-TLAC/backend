"""Minimal mock supplier registration and product import."""
from __future__ import annotations

import secrets
from itertools import count
from typing import Dict, List, Optional


SUPPLIERS: Dict[int, dict] = {
    1: {
        "id": 1,
        "name": "FilamentCo",
        "address": "Bratislava",
        "contact": "info@filament.co",
        "username": "filamentco",
        "password": "demo1234",
        "products": [
            {"externalId": "fc-pla-black", "name": "PLA Black",  "price": 18.0},
            {"externalId": "fc-abs-blue",  "name": "ABS Blue",   "price": 20.0},
            {"externalId": "fc-petg-red",  "name": "PETG Red",   "price": 22.0},
        ],
    },
}
_ids = count(start=2)


def list_suppliers() -> List[dict]:
    return list(SUPPLIERS.values())


def register_supplier(data: dict) -> dict:
    sid = next(_ids)
    name = data.get("name", f"Supplier{sid}")
    record = {
        "id": sid,
        "name": name,
        "address": data.get("address", ""),
        "contact": data.get("contact", ""),
        "username": name.lower().replace(" ", "") or f"supplier{sid}",
        "password": secrets.token_hex(4),
    }
    SUPPLIERS[sid] = record
    return record


def import_products(supplier_id: int, link: Optional[str]) -> dict:
    supplier = SUPPLIERS.get(supplier_id)
    if supplier is None:
        return {"success": False, "error": "supplier_not_found"}
    if not link or not link.startswith("http"):
        return {"success": False, "error": "invalid_link"}
    if "denied" in link:
        return {"success": False, "error": "access_denied"}
    if "fail" in link:
        return {"success": False, "error": "import_failed"}
    products = [
        {"externalId": "ext-1", "name": "PLA Green",   "price": 18.0, "supplierId": supplier_id},
        {"externalId": "ext-2", "name": "PETG Yellow", "price": 22.0, "supplierId": supplier_id},
        {"externalId": "ext-3", "name": "ABS Black",   "price": 20.0, "supplierId": supplier_id},
    ]
    return {"success": True, "imported": len(products), "products": products}
