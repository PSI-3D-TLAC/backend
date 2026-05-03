\
\
\
\
\
from __future__ import annotations

import secrets
from typing import Dict, List, Optional

                     
USERS: List[dict] = [
                                                              
    {"id": 1, "name": "Test Customer",   "email": "customer@test.com", "password": "1234", "role": "Customer"},
    {"id": 2, "name": "Test Admin",      "email": "admin@test.com",    "password": "1234", "role": "Admin"},
    {"id": 3, "name": "Test Warehouse",  "email": "warehouse@test.com","password": "1234", "role": "WarehouseWorker"},
    {"id": 4, "name": "Test Manager",    "email": "manager@test.com",  "password": "1234", "role": "Manager"},
    {"id": 5, "name": "Test Support",    "email": "support@test.com",  "password": "1234", "role": "Support"},
                                                                   
    {"id": 6, "name": "Erik Carrier",    "email": "carrier@example.com","password": "test","role": "Carrier"},
    {"id": 7, "name": "Gabo Employee",   "email": "emp@example.com",   "password": "test", "role": "Employee"},
]

ROLES: List[str] = [
    "Customer", "Admin", "Employee", "WarehouseWorker", "Manager", "Carrier", "Support",
]

SESSIONS: Dict[str, int] = {}

def _public(user: dict) -> dict:
    return {k: v for k, v in user.items() if k != "password"}

def login(email: str, password: str) -> Optional[dict]:
    for u in USERS:
        if u["email"] == email and u["password"] == password:
            token = secrets.token_hex(8)
            SESSIONS[token] = u["id"]
            return {"token": token, "user": _public(u)}
    return None

def logout(token: str) -> bool:
    return SESSIONS.pop(token, None) is not None

def list_users() -> List[dict]:
    return [_public(u) for u in USERS]

def list_roles() -> List[str]:
    return list(ROLES)
