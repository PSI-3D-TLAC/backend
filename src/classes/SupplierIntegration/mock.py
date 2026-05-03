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
        "registrationStatus": "registered",
        "products": [
            {"externalId": "fc-pla-black", "name": "PLA Black", "price": 18.0, "supplierId": 1},
            {"externalId": "fc-abs-blue",  "name": "ABS Blue",  "price": 20.0, "supplierId": 1},
            {"externalId": "fc-petg-red",  "name": "PETG Red",  "price": 22.0, "supplierId": 1},
        ],
    },
}
_ids = count(start=2)


def list_suppliers() -> List[dict]:
    return list(SUPPLIERS.values())


def get_supplier(supplier_id: int) -> Optional[dict]:
    return SUPPLIERS.get(supplier_id)


def supplier_exists(supplier_id: int) -> bool:
    return supplier_id in SUPPLIERS


def register_supplier(data: dict) -> dict:
    name = (data.get("name") or "").strip()
    if not name:
        return {"error": "validation_error", "message": "Supplier name is required."}
    sid = next(_ids)
    record = {
        "id": sid,
        "name": name,
        "address": (data.get("address") or "").strip(),
        "contact": (data.get("contact") or "").strip(),
        "username": name.lower().replace(" ", "") or f"supplier{sid}",
        "password": secrets.token_hex(4),
        "registrationStatus": "registered",
        "products": [],
    }
    SUPPLIERS[sid] = record
    return record


def import_products(supplier_id: int, link: Optional[str] = None) -> dict:
    supplier = SUPPLIERS.get(supplier_id)
    if supplier is None:
        return {"success": False, "error": "supplier_not_found",
                "message": f"Supplier #{supplier_id} does not exist."}
    if link:
        if not link.startswith("http"):
            return {"success": False, "error": "invalid_link",
                    "message": "Catalog link must start with http(s)."}
        if "denied" in link:
            return {"success": False, "error": "access_denied",
                    "message": "Access to supplier catalog denied."}
        if "fail" in link:
            return {"success": False, "error": "import_failed",
                    "message": "Supplier import failed."}
    products = [
        {"externalId": f"ext-{supplier_id}-1", "name": "PLA Green",   "price": 18.0, "supplierId": supplier_id},
        {"externalId": f"ext-{supplier_id}-2", "name": "PETG Yellow", "price": 22.0, "supplierId": supplier_id},
        {"externalId": f"ext-{supplier_id}-3", "name": "ABS Black",   "price": 20.0, "supplierId": supplier_id},
    ]
    existing = {p.get("externalId") for p in supplier.get("products", [])}
    for p in products:
        if p["externalId"] not in existing:
            supplier.setdefault("products", []).append(p)
    return {"success": True, "supplierId": supplier_id, "imported": len(products), "products": products}
