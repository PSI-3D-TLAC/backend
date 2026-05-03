from __future__ import annotations

from typing import Optional

from ..classes.Inventory import mock as inventory_mock

def list_materials(query: Optional[str] = None) -> list:
    return inventory_mock.list_materials(query)

def get_material(material_id) -> Optional[dict]:
    if material_id is None:
        return None
    for m in inventory_mock.list_materials():
        if str(m.get("id")) == str(material_id):
            return m
    return None

def validate(material_id) -> Optional[dict]:
    if get_material(material_id) is None:
        return {"error": f"Unknown materialId {material_id!r}"}
    return None

def apply_multiplier(base_price: float, material_id) -> float:
    material = get_material(material_id) or {}
    multiplier = float(material.get("priceMultiplier", 1.0))
    return round(float(base_price) * multiplier, 2)
