"""HTTP routes for the 3D PrintHub mock backend.

Routes are intentionally thin and just delegate to the per-package ``mock``
modules. They exist purely to let the frontend call endpoints without errors.
"""
from __future__ import annotations

from functools import wraps
from typing import Iterable

from flask import Blueprint, jsonify, request

from ..classes.Catalog import mock as catalog_mock
from ..classes.Delivery import mock as delivery_mock
from ..classes.Inventory import mock as inventory_mock
from ..classes.OrderManagment import mock as order_mock
from ..classes.Payment import mock as payment_mock
from ..classes.SupplierIntegration import mock as supplier_mock
from ..classes.Support import mock as support_mock
from ..classes.UserManagment import mock as user_mock


# ---------------------------------------------------------------- role guard
def require_role(*allowed: str):
    """Tiny role guard. Reads ``X-User-Role`` header and 403s if it doesn't match.

    Mock-only: there's no real auth — the frontend just sends the role it stored
    after login. Good enough for school-project testing.
    """
    allowed_set = {r.lower() for r in allowed}

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = (request.headers.get("X-User-Role") or "").strip().lower()
            if role not in allowed_set:
                return (
                    jsonify(
                        success=False,
                        error="forbidden",
                        message="You do not have permission to perform this action.",
                        allowedRoles=list(allowed),
                    ),
                    403,
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


# ---------------------------------------------------------------- health
health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify(status="ok")


# ---------------------------------------------------------------- auth
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    result = user_mock.login(data.get("email", ""), data.get("password", ""))
    if result is None:
        return jsonify(success=False, error="invalid_credentials"), 401
    return jsonify(success=True, **result)


@auth_bp.post("/logout")
def logout():
    data = request.get_json(silent=True) or {}
    token = data.get("token") or request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    return jsonify(success=user_mock.logout(token))


# ---------------------------------------------------------------- users
users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.get("")
def list_users():
    return jsonify(users=user_mock.list_users(), roles=user_mock.list_roles())


# ---------------------------------------------------------------- catalog
catalog_bp = Blueprint("catalog", __name__, url_prefix="/catalog")


@catalog_bp.get("/products")
def list_products():
    active = request.args.get("active") in ("1", "true", "True")
    return jsonify(products=catalog_mock.list_products(active_only=active))


@catalog_bp.post("/products")
@require_role("Admin")
def create_product():
    product = catalog_mock.create_product(request.get_json(silent=True) or {})
    return jsonify(success=True, product=product), 201


@catalog_bp.get("/products/<int:pid>")
def get_product(pid: int):
    product = catalog_mock.get_product(pid)
    if product is None:
        return jsonify(success=False, error="not_found"), 404
    return jsonify(success=True, product=product)


@catalog_bp.put("/products/<int:pid>")
@require_role("Admin")
def update_product(pid: int):
    product = catalog_mock.update_product(pid, request.get_json(silent=True) or {})
    if product is None:
        return jsonify(success=False, error="not_found"), 404
    return jsonify(success=True, product=product)


@catalog_bp.delete("/products/<int:pid>")
@require_role("Admin")
def delete_product(pid: int):
    if not catalog_mock.delete_product(pid):
        return jsonify(success=False, error="not_found"), 404
    return jsonify(success=True)


# ---------------------------------------------------------------- inventory
inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@inventory_bp.get("/materials")
def list_materials():
    q = request.args.get("q")
    return jsonify(materials=inventory_mock.list_materials(q))


# ---------------------------------------------------------------- orders
orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


@orders_bp.get("")
def list_orders():
    customer = request.args.get("customerId", type=int)
    return jsonify(
        orders=order_mock.list_orders(customer_id=customer),
        statuses=order_mock.ORDER_STATUSES,
    )


@orders_bp.get("/options")
def order_options():
    """Return available delivery methods, payment types and statuses."""
    return jsonify(success=True, **order_mock.list_options())


@orders_bp.post("")
@require_role("Customer")
def create_order():
    data = request.get_json(silent=True) or {}
    # Validate optional new fields if provided.
    delivery = data.get("deliveryMethod")
    if delivery is not None and delivery not in order_mock.DELIVERY_METHODS:
        return jsonify(
            success=False,
            error=f"Unknown deliveryMethod {delivery!r}",
            allowed=list(order_mock.DELIVERY_METHODS.keys()),
        ), 400
    payment = data.get("paymentType")
    if payment is not None and payment not in order_mock.PAYMENT_TYPES:
        return jsonify(
            success=False,
            error=f"Unknown paymentType {payment!r}",
            allowed=list(order_mock.PAYMENT_TYPES.keys()),
        ), 400
    order = order_mock.create_order(data)
    return jsonify(success=True, order=order), 201


@orders_bp.get("/<int:oid>")
def get_order(oid: int):
    order = order_mock.get_order(oid)
    if order is None:
        return jsonify(success=False, error="not_found"), 404
    return jsonify(success=True, order=order)


@orders_bp.put("/<int:oid>/status")
@require_role("Support", "Manager", "Admin")
def update_order_status(oid: int):
    data = request.get_json(silent=True) or {}
    result = order_mock.update_status(oid, data.get("status", ""))
    if result is None:
        return jsonify(success=False, error="not_found"), 404
    if "error" in result:
        return jsonify(success=False, **result), 400
    return jsonify(success=True, order=result)


# ---------------------------------------------------------------- payments
payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


@payments_bp.post("/pay")
@require_role("Customer")
def pay():
    result = payment_mock.pay(request.get_json(silent=True) or {})
    status_code = 200 if result["success"] else 402
    return jsonify(**result), status_code


# ---------------------------------------------------------------- delivery
delivery_bp = Blueprint("delivery", __name__, url_prefix="/delivery")


@delivery_bp.get("/options")
def delivery_options():
    return jsonify(success=True, **delivery_mock.list_options())


@delivery_bp.post("/shipments")
@require_role("Customer", "Manager", "Admin")
def create_shipment():
    shipment = delivery_mock.create_shipment(request.get_json(silent=True) or {})
    return jsonify(success=True, shipment=shipment), 201


@delivery_bp.put("/shipments/<int:sid>/status")
def update_shipment_status(sid: int):
    data = request.get_json(silent=True) or {}
    result = delivery_mock.update_shipment_status(sid, data.get("status", ""))
    if result is None:
        return jsonify(success=False, error="not_found"), 404
    if "error" in result:
        return jsonify(success=False, **result), 400
    return jsonify(success=True, shipment=result)


# ---------------------------------------------------------------- support
support_bp = Blueprint("support", __name__, url_prefix="/support")


def _current_user() -> dict:
    """Tiny helper: read the mock identity from request headers."""
    return {
        "id": (request.headers.get("X-User-Id") or "").strip() or None,
        "role": (request.headers.get("X-User-Role") or "").strip() or None,
    }


@support_bp.get("/requests")
def list_requests():
    """List support requests.

    - Support/Admin: all requests.
    - Customer: only their own (filtered by X-User-Id).
    - Anyone else: 403.
    """
    user = _current_user()
    role = (user.get("role") or "").lower()
    if role in ("support", "admin"):
        items = support_mock.list_requests()
    elif role == "customer":
        items = support_mock.list_requests(customer_id=user.get("id"))
    else:
        return jsonify(success=False, error="forbidden"), 403
    return jsonify(requests=items, statuses=support_mock.REQUEST_STATUSES)


@support_bp.post("/requests")
@require_role("Customer")
def create_request():
    record = support_mock.create_request(request.get_json(silent=True) or {}, user=_current_user())
    return jsonify(success=True, request=record), 201


@support_bp.get("/requests/<int:rid>")
def get_request_detail(rid: int):
    user = _current_user()
    role = (user.get("role") or "").lower()
    record = support_mock.get_request(rid)
    if record is None:
        return jsonify(success=False, error="not_found"), 404
    if role == "customer" and str(record.get("customerId")) != str(user.get("id")):
        return jsonify(success=False, error="forbidden"), 403
    if role not in ("support", "admin", "customer"):
        return jsonify(success=False, error="forbidden"), 403
    return jsonify(success=True, request=record)


@support_bp.patch("/requests/<int:rid>/status")
@require_role("Support", "Admin")
def patch_request_status(rid: int):
    data = request.get_json(silent=True) or {}
    result = support_mock.update_request_status(
        rid,
        data.get("status", ""),
        comment=data.get("comment", "") or data.get("response", ""),
        user=_current_user(),
    )
    if result is None:
        return jsonify(success=False, error="not_found"), 404
    if isinstance(result, dict) and "error" in result:
        return jsonify(success=False, **result), 400
    return jsonify(success=True, request=result)


# Kept for backwards compatibility with existing frontend code.
@support_bp.put("/requests/<int:rid>/status")
@require_role("Support", "Admin")
def update_request_status(rid: int):
    return patch_request_status(rid)


@support_bp.get("/complaints")
def list_complaints():
    user = _current_user()
    role = (user.get("role") or "").lower()
    if role in ("support", "admin"):
        items = support_mock.list_complaints()
    elif role == "customer":
        items = support_mock.list_complaints(customer_id=user.get("id"))
    else:
        return jsonify(success=False, error="forbidden"), 403
    return jsonify(
        complaints=items,
        reasons=support_mock.COMPLAINT_REASONS,
        statuses=support_mock.COMPLAINT_STATUSES,
    )


@support_bp.post("/complaints")
@require_role("Customer")
def create_complaint():
    result = support_mock.create_complaint(request.get_json(silent=True) or {}, user=_current_user())
    if "error" in result:
        return jsonify(success=False, **result), 400
    return jsonify(success=True, complaint=result), 201


@support_bp.get("/complaints/<int:cid>")
def get_complaint_detail(cid: int):
    user = _current_user()
    role = (user.get("role") or "").lower()
    record = support_mock.get_complaint(cid)
    if record is None:
        return jsonify(success=False, error="not_found"), 404
    if role == "customer" and str(record.get("customerId")) != str(user.get("id")):
        return jsonify(success=False, error="forbidden"), 403
    if role not in ("support", "admin", "customer"):
        return jsonify(success=False, error="forbidden"), 403
    return jsonify(success=True, complaint=record)


@support_bp.patch("/complaints/<int:cid>/status")
@require_role("Support", "Admin")
def patch_complaint_status(cid: int):
    data = request.get_json(silent=True) or {}
    result = support_mock.update_complaint_status(
        cid,
        data.get("status", ""),
        comment=data.get("comment", "") or data.get("response", ""),
        user=_current_user(),
    )
    if result is None:
        return jsonify(success=False, error="not_found"), 404
    if isinstance(result, dict) and "error" in result:
        return jsonify(success=False, **result), 400
    return jsonify(success=True, complaint=result)


# ---------------------------------------------------------------- suppliers
suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")


@suppliers_bp.get("")
def list_suppliers():
    return jsonify(suppliers=supplier_mock.list_suppliers())


@suppliers_bp.post("")
@require_role("Manager", "Admin")
def register_supplier():
    record = supplier_mock.register_supplier(request.get_json(silent=True) or {})
    return jsonify(success=True, supplier=record), 201


@suppliers_bp.post("/<int:sid>/import-products")
@require_role("Manager", "Admin")
def import_supplier_products(sid: int):
    data = request.get_json(silent=True) or {}
    result = supplier_mock.import_products(sid, data.get("link"))
    status_code = 200 if result.get("success") else 400
    return jsonify(**result), status_code


ALL_BLUEPRINTS = [
    health_bp,
    auth_bp,
    users_bp,
    catalog_bp,
    inventory_bp,
    orders_bp,
    payments_bp,
    delivery_bp,
    support_bp,
    suppliers_bp,
]
