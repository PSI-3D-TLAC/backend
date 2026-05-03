from __future__ import annotations

from functools import wraps

from flask import Blueprint, jsonify, request

from ..classes.Catalog import mock as catalog_mock
from ..classes.Delivery import mock as delivery_mock
from ..classes.OrderManagment import mock as order_mock
from ..classes.Payment import mock as payment_mock
from ..classes.SupplierIntegration import mock as supplier_mock
from ..classes.Support import mock as support_mock
from ..classes.UserManagment import mock as user_mock
from ..use_cases import (
    UC01_create_order,
    UC02_select_material,
    UC03_choose_delivery,
    UC04_choose_payment,
    UC05_track_order_status,
    UC06_support_dashboard,
)

def require_role(*allowed: str):
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

health_bp = Blueprint("health", __name__)

@health_bp.get("/health")
def health():
    return jsonify(status="ok")

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

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.get("")
def list_users():
    return jsonify(users=user_mock.list_users(), roles=user_mock.list_roles())

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

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")

@inventory_bp.get("/materials")
def list_materials():
    q = request.args.get("q")
    return jsonify(materials=UC02_select_material.list_materials(q))

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

@orders_bp.get("")
def list_orders():
    customer = request.args.get("customerId", type=int)
    return jsonify(
        orders=UC05_track_order_status.list_orders(customer_id=customer),
        statuses=UC05_track_order_status.list_statuses(),
    )

@orders_bp.get("/options")
def order_options():
    return jsonify(success=True, **order_mock.list_options())

@orders_bp.post("")
@require_role("Customer")
def create_order():
    data = request.get_json(silent=True) or {}
    if data.get("deliveryMethod") is not None:
        err = UC03_choose_delivery.validate(data.get("deliveryMethod"))
        if err:
            return jsonify(success=False, **err), 400
    if data.get("paymentType") is not None:
        err = UC04_choose_payment.validate(data.get("paymentType"))
        if err:
            return jsonify(success=False, **err), 400
    delivery = data.get("delivery")
    if delivery is not None and not isinstance(delivery, dict):
        return jsonify(success=False, error="invalid_delivery",
                       message="delivery must be an object"), 400
    if isinstance(delivery, dict):
        ship_check = delivery_mock.create_shipment({
            "orderId": 0,
            "carrier": delivery.get("carrier"),
            "deliveryType": delivery.get("deliveryType"),
            "address": delivery.get("address"),
        })
        if isinstance(ship_check, dict) and "error" in ship_check:
            return jsonify(success=False, **ship_check), 400
        delivery_mock.SHIPMENTS.pop(ship_check["id"], None)
    order = UC01_create_order.create(data)
    response = {"success": True, "order": order}
    if isinstance(delivery, dict):
        shipment = delivery_mock.create_shipment({
            "orderId": order.get("id"),
            "carrier": delivery.get("carrier"),
            "deliveryType": delivery.get("deliveryType"),
            "address": delivery.get("address"),
        })
        response["shipment"] = shipment
    return jsonify(**response), 201

@orders_bp.get("/<int:oid>")
def get_order(oid: int):
    order = UC05_track_order_status.get_order(oid)
    if order is None:
        return jsonify(success=False, error="not_found"), 404
    return jsonify(success=True, order=order)

@orders_bp.put("/<int:oid>/status")
@require_role("Support", "Manager", "Admin")
def update_order_status(oid: int):
    data = request.get_json(silent=True) or {}
    result = UC05_track_order_status.update_status(oid, data.get("status", ""))
    if result is None:
        return jsonify(success=False, error="not_found"), 404
    if "error" in result:
        return jsonify(success=False, **result), 400
    return jsonify(success=True, order=result)

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")

@payments_bp.post("/pay")
@require_role("Customer")
def pay():
    result = payment_mock.pay(request.get_json(silent=True) or {})
    status_code = 200 if result["success"] else 402
    return jsonify(**result), status_code

delivery_bp = Blueprint("delivery", __name__, url_prefix="/delivery")

@delivery_bp.get("/options")
def delivery_options():
    return jsonify(success=True, **delivery_mock.list_options())

@delivery_bp.post("/shipments")
@require_role("Customer", "Manager", "Admin")
def create_shipment():
    result = delivery_mock.create_shipment(request.get_json(silent=True) or {})
    if isinstance(result, dict) and "error" in result:
        return jsonify(success=False, **result), 400
    return jsonify(success=True, shipment=result), 201

@delivery_bp.put("/shipments/<int:sid>/status")
def update_shipment_status(sid: int):
    data = request.get_json(silent=True) or {}
    result = delivery_mock.update_shipment_status(sid, data.get("status", ""))
    if result is None:
        return jsonify(success=False, error="not_found"), 404
    if "error" in result:
        return jsonify(success=False, **result), 400
    return jsonify(success=True, shipment=result)

support_bp = Blueprint("support", __name__, url_prefix="/support")

def _current_user() -> dict:
    return {
        "id": (request.headers.get("X-User-Id") or "").strip() or None,
        "role": (request.headers.get("X-User-Role") or "").strip() or None,
    }

def _can_view(record: dict, user: dict) -> bool:
    role = (user.get("role") or "").lower()
    if role in ("support", "admin"):
        return True
    if role == "customer":
        return str(record.get("customerId")) == str(user.get("id"))
    return False

@support_bp.get("/requests")
def list_requests():
    user = _current_user()
    items = UC06_support_dashboard.list_requests(user.get("role"), user.get("id"))
    if items is None:
        return jsonify(success=False, error="forbidden"), 403
    return jsonify(requests=items, statuses=UC06_support_dashboard.request_statuses())

@support_bp.post("/requests")
@require_role("Customer")
def create_request():
    record = support_mock.create_request(request.get_json(silent=True) or {}, user=_current_user())
    return jsonify(success=True, request=record), 201

@support_bp.get("/requests/<int:rid>")
def get_request_detail(rid: int):
    record = UC06_support_dashboard.get_request(rid)
    if record is None:
        return jsonify(success=False, error="not_found"), 404
    if not _can_view(record, _current_user()):
        return jsonify(success=False, error="forbidden"), 403
    return jsonify(success=True, request=record)

@support_bp.patch("/requests/<int:rid>/status")
@require_role("Support", "Admin")
def patch_request_status(rid: int):
    data = request.get_json(silent=True) or {}
    result = UC06_support_dashboard.update_request_status(
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

@support_bp.put("/requests/<int:rid>/status")
@require_role("Support", "Admin")
def update_request_status(rid: int):
    return patch_request_status(rid)

@support_bp.get("/complaints")
def list_complaints():
    user = _current_user()
    items = UC06_support_dashboard.list_complaints(user.get("role"), user.get("id"))
    if items is None:
        return jsonify(success=False, error="forbidden"), 403
    return jsonify(
        complaints=items,
        reasons=support_mock.COMPLAINT_REASONS,
        statuses=UC06_support_dashboard.complaint_statuses(),
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
    record = UC06_support_dashboard.get_complaint(cid)
    if record is None:
        return jsonify(success=False, error="not_found"), 404
    if not _can_view(record, _current_user()):
        return jsonify(success=False, error="forbidden"), 403
    return jsonify(success=True, complaint=record)

@support_bp.patch("/complaints/<int:cid>/status")
@require_role("Support", "Admin")
def patch_complaint_status(cid: int):
    data = request.get_json(silent=True) or {}
    result = UC06_support_dashboard.update_complaint_status(
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

suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")

@suppliers_bp.get("")
def list_suppliers():
    return jsonify(suppliers=supplier_mock.list_suppliers())

@suppliers_bp.get("/<int:sid>")
def get_supplier_detail(sid: int):
    record = supplier_mock.get_supplier(sid)
    if record is None:
        return jsonify(success=False, error="supplier_not_found",
                       message=f"Supplier #{sid} does not exist."), 404
    return jsonify(success=True, supplier=record)

@suppliers_bp.post("")
@require_role("Manager", "Admin")
def register_supplier():
    result = supplier_mock.register_supplier(request.get_json(silent=True) or {})
    if "error" in result:
        return jsonify(success=False, **result), 400
    return jsonify(
        success=True,
        supplier=result,
        supplierId=result["id"],
        registrationStatus=result.get("registrationStatus", "registered"),
        message=f"Supplier '{result['name']}' registered with ID #{result['id']}.",
    ), 201

@suppliers_bp.post("/register")
@require_role("Manager", "Admin")
def register_supplier_full():
    result = supplier_mock.register_supplier_full(request.get_json(silent=True) or {})
    if not result.get("success"):
        return jsonify(result), 400
    payload = {
        "success": True,
        "supplier": result["supplier"],
        "credentials": result["credentials"],
        "importedProducts": result.get("importedProducts", []),
        "importStatus": result.get("importStatus", "skipped"),
    }
    if result.get("importStatus") == "failed":
        payload["importMessage"] = result.get("importMessage")
        payload["importError"] = result.get("importError")
        payload["message"] = (
            f"Supplier #{result['supplier']['id']} created, "
            f"but product import failed: {result.get('importMessage')}"
        )
    else:
        payload["message"] = (
            f"Supplier '{result['supplier']['companyName']}' "
            f"registered with ID #{result['supplier']['id']}."
        )
    return jsonify(payload), 201

@suppliers_bp.post("/import-products")
@suppliers_bp.post("/<int:sid>/import-products")
@require_role("Manager", "Admin")
def import_supplier_products(sid: int | None = None):
    data = request.get_json(silent=True) or {}
    if sid is None:
        raw = data.get("supplierId", data.get("supplier_id"))
        try:
            sid = int(raw) if raw is not None and str(raw).strip() != "" else None
        except (TypeError, ValueError):
            sid = None
        if sid is None:
            return jsonify(success=False, error="validation_error",
                           message="supplierId is required."), 400
    result = supplier_mock.import_products(sid, data.get("link"))
    if result.get("success"):
        return jsonify(**result), 200
    status_code = 404 if result.get("error") == "supplier_not_found" else 400
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
