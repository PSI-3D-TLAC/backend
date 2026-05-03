"""Minimal mock inventory: list of filaments/materials."""
from __future__ import annotations

from typing import Dict, List, Optional


MATERIALS: Dict[int, dict] = {
    1: {"id": 1, "name": "PLA",  "type": "PLA",  "color": "Black", "quantity": 50, "status": "Available", "location": "A-1", "supplierId": 1, "properties": {"diameter": 1.75, "temp": 200}},
    2: {"id": 2, "name": "ABS",  "type": "ABS",  "color": "Blue",  "quantity":  5, "status": "Low Stock", "location": "B-2", "supplierId": 1, "properties": {"diameter": 1.75, "temp": 240}},
    3: {"id": 3, "name": "PETG", "type": "PETG", "color": "Red",   "quantity":  0, "status": "Expected",  "location": "B-1", "supplierId": 1, "properties": {"diameter": 1.75, "temp": 235}},
}


def list_materials(query: Optional[str] = None) -> List[dict]:
    items = list(MATERIALS.values())
    if query:
        q = query.lower()
        items = [m for m in items if q in m["name"].lower() or q in m["type"].lower() or q in m["color"].lower()]
    return items


def get_material(material_id: int) -> Optional[dict]:
    return MATERIALS.get(material_id)
