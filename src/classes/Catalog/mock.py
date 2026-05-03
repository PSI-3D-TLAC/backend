"""Minimal mock catalog: dict-based product CRUD."""
from __future__ import annotations

from itertools import count
from typing import Dict, List, Optional


_ids = count(start=5)

PRODUCTS: Dict[int, dict] = {
    1: {"id": 1, "name": "Phone Stand",  "description": "Adjustable phone holder",      "price":  9.50, "material": "PLA",  "availability": "Available", "category": "Office", "isActive": True,  "image": "/img/stand.png",  "modelRef": "stand.stl"},
    2: {"id": 2, "name": "Gear Model",   "description": "Mechanical gear demo model",   "price": 12.00, "material": "PETG", "availability": "Available", "category": "Tech",   "isActive": True,  "image": "/img/gear.png",   "modelRef": "gear.stl"},
    3: {"id": 3, "name": "Mini Figure",  "description": "Collectible mini figurine",    "price":  7.50, "material": "PLA",  "availability": "Low Stock", "category": "Toys",   "isActive": True,  "image": "/img/mini.png",   "modelRef": "mini.stl"},
    4: {"id": 4, "name": "Vase Classic", "description": "Decorative spiral vase",       "price": 14.90, "material": "PLA",  "availability": "Available", "category": "Home",   "isActive": True,  "image": "/img/vase.png",   "modelRef": "vase.stl"},
}


def list_products(active_only: bool = False) -> List[dict]:
    items = list(PRODUCTS.values())
    if active_only:
        items = [p for p in items if p.get("isActive")]
    return items


def get_product(product_id: int) -> Optional[dict]:
    return PRODUCTS.get(product_id)


def create_product(data: dict) -> dict:
    pid = next(_ids)
    product = {
        "id": pid,
        "name": data.get("name", "Unnamed"),
        "description": data.get("description", ""),
        "price": float(data.get("price", 0.0)),
        "material": data.get("material", "PLA"),
        "availability": data.get("availability", "Available"),
        "category": data.get("category", "Other"),
        "isActive": bool(data.get("isActive", True)),
        "image": data.get("image"),
        "modelRef": data.get("modelRef"),
    }
    PRODUCTS[pid] = product
    return product


def update_product(product_id: int, data: dict) -> Optional[dict]:
    product = PRODUCTS.get(product_id)
    if product is None:
        return None
    for key in ("name", "description", "price", "material", "availability", "category", "isActive", "image", "modelRef"):
        if key in data:
            product[key] = data[key]
    return product


def delete_product(product_id: int) -> bool:
    return PRODUCTS.pop(product_id, None) is not None
