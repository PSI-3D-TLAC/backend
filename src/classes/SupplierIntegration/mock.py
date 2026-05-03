from __future__ import annotations

import secrets
from itertools import count
from typing import Dict, List, Optional, Tuple

SUPPLIERS: Dict[int, dict] = {
    1: {
        "id": 1,
        "companyName": "FilamentCo",
        "contactPerson": "Jane Filament",
        "email": "info@filament.co",
        "phone": "+421900000111",
        "address": "Bratislava, Slovakia",
        "externalCatalogLink": None,
        "username": "supplier1",
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

REQUIRED_FIELDS = ("companyName", "contactPerson", "email", "phone", "address")

def list_suppliers() -> List[dict]:
    return list(SUPPLIERS.values())

def get_supplier(supplier_id: int) -> Optional[dict]:
    return SUPPLIERS.get(supplier_id)

def supplier_exists(supplier_id: int) -> bool:
    return supplier_id in SUPPLIERS

def validate_supplier_data(data: dict) -> Optional[dict]:
    missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]
    if missing:
        return {"error": "validation_error",
                "message": "Missing required fields: " + ", ".join(missing),
                "missing": missing}
    email = str(data.get("email", "")).strip()
    if "@" not in email:
        return {"error": "validation_error",
                "message": "Email must contain '@'.",
                "field": "email"}
    return None

def generate_supplier_credentials(supplier_id: int, company_name: str) -> dict:
    base = "".join(ch for ch in company_name.lower() if ch.isalnum())
    username = base or f"supplier{supplier_id}"
    if username in {s.get("username") for s in SUPPLIERS.values()}:
        username = f"supplier{supplier_id}"
    return {"username": username, "password": secrets.token_hex(4)}

def create_supplier_profile(data: dict) -> dict:
    sid = next(_ids)
    creds = generate_supplier_credentials(sid, str(data.get("companyName", "")).strip())
    record = {
        "id": sid,
        "companyName": str(data.get("companyName", "")).strip(),
        "contactPerson": str(data.get("contactPerson", "")).strip(),
        "email": str(data.get("email", "")).strip(),
        "phone": str(data.get("phone", "")).strip(),
        "address": str(data.get("address", "")).strip(),
        "externalCatalogLink": (str(data.get("externalCatalogLink", "")).strip() or None),
        "username": creds["username"],
        "password": creds["password"],
        "registrationStatus": "registered",
        "products": [],
    }
    SUPPLIERS[sid] = record
    return record

def connect_to_external_catalog(link: str) -> Optional[dict]:
    if not link:
        return None
    if not (link.startswith("http://") or link.startswith("https://")):
        return {"error": "invalid_link",
                "message": "External catalog link must start with http(s)://"}
    if "denied" in link:
        return {"error": "access_denied",
                "message": "Access to supplier catalog denied."}
    if "fail" in link:
        return {"error": "import_failed",
                "message": "Supplier import failed."}
    return None

def fetch_supplier_products(supplier_id: int, link: str) -> List[dict]:
    return [
        {"externalId": f"ext-{supplier_id}-1", "name": "PLA Green",   "price": 18.0},
        {"externalId": f"ext-{supplier_id}-2", "name": "PETG Yellow", "price": 22.0},
        {"externalId": f"ext-{supplier_id}-3", "name": "ABS Black",   "price": 20.0},
    ]

def link_products_to_supplier(supplier_id: int, products: List[dict]) -> List[dict]:
    supplier = SUPPLIERS.get(supplier_id)
    if supplier is None:
        return []
    existing = {p.get("externalId") for p in supplier.get("products", [])}
    linked: List[dict] = []
    for p in products:
        item = {**p, "supplierId": supplier_id}
        if item.get("externalId") in existing:
            continue
        supplier.setdefault("products", []).append(item)
        existing.add(item.get("externalId"))
        linked.append(item)
    return linked

def import_supplier_products(supplier_id: int, link: Optional[str]) -> Tuple[List[dict], Optional[dict]]:
    if not link:
        return [], None
    err = connect_to_external_catalog(link)
    if err is not None:
        return [], err
    fetched = fetch_supplier_products(supplier_id, link)
    linked = link_products_to_supplier(supplier_id, fetched)
    return linked, None

def register_supplier_full(data: dict) -> dict:
    err = validate_supplier_data(data)
    if err is not None:
        return {"success": False, **err}
    supplier = create_supplier_profile(data)
    link = supplier.get("externalCatalogLink")
    imported, import_err = import_supplier_products(supplier["id"], link)
    response: dict = {
        "success": True,
        "supplier": {
            "id": supplier["id"],
            "companyName": supplier["companyName"],
            "email": supplier["email"],
        },
        "supplierFull": supplier,
        "credentials": {
            "username": supplier["username"],
            "password": supplier["password"],
        },
        "importedProducts": imported,
    }
    if import_err is not None:
        response["importStatus"] = "failed"
        response["importMessage"] = import_err.get("message")
        response["importError"] = import_err.get("error")
    elif link:
        response["importStatus"] = "ok"
    else:
        response["importStatus"] = "skipped"
    return response

def register_supplier(data: dict) -> dict:
    company = (data.get("companyName") or data.get("name") or "").strip()
    if not company:
        return {"error": "validation_error", "message": "Supplier name is required."}
    payload = {
        "companyName": company,
        "contactPerson": (data.get("contactPerson") or data.get("contact") or "n/a").strip() or "n/a",
        "email": (data.get("email") or data.get("contact") or "n/a@example.com").strip() or "n/a@example.com",
        "phone": (data.get("phone") or "n/a").strip() or "n/a",
        "address": (data.get("address") or "n/a").strip() or "n/a",
        "externalCatalogLink": (data.get("externalCatalogLink") or "").strip() or None,
    }
    if "@" not in payload["email"]:
        payload["email"] = "n/a@example.com"
    supplier = create_supplier_profile(payload)
    legacy = dict(supplier)
    legacy["name"] = supplier["companyName"]
    legacy["contact"] = supplier["email"]
    SUPPLIERS[supplier["id"]] = legacy
    return legacy

def import_products(supplier_id: int, link: Optional[str] = None) -> dict:
    supplier = SUPPLIERS.get(supplier_id)
    if supplier is None:
        return {"success": False, "error": "supplier_not_found",
                "message": f"Supplier #{supplier_id} does not exist."}
    if link:
        err = connect_to_external_catalog(link)
        if err is not None:
            return {"success": False, **err}
    fetched = fetch_supplier_products(supplier_id, link or "")
    linked = link_products_to_supplier(supplier_id, fetched)
    return {"success": True, "supplierId": supplier_id,
            "imported": len(linked), "products": linked}
