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
    UC01_inventory_management,
    UC02_create_order,
    UC03_payment_processing,
    UC05_customer_request,
    UC06_delivery_processing,
    UC07_order_processing,
    UC09_complaint_handling,
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

def _serialize_shipment(shipment: dict | None) -> dict | None:
    if shipment is None:
        return None
    payload = dict(shipment)
    payload["status"] = delivery_mock.normalize_status(payload.get("status"))
    payload["allowedNextStatuses"] = delivery_mock.allowed_next_statuses(payload.get("status"))
    return payload

def _serialize_order(order: dict | None) -> dict | None:
    if order is None:
        return None
    payload = dict(order)
    payload["status"] = order_mock.normalize_status(payload.get("status"))
    payload["allowedNextStatuses"] = order_mock.allowed_next_statuses(payload.get("status"))
    shipment = delivery_mock.get_shipment_by_order_id(order.get("id"))
    if shipment is not None:
        payload["shipment"] = _serialize_shipment(shipment)
    return payload

def _shipment_target_for_order_status(order_status: str) -> str | None:
    mapping = {
        "Pripravená na odoslanie": "Neodoslaná",
        "Odoslaná": "Odoslaná",
        "Doručená": "Doručená",
    }
    return mapping.get(order_status)

def _ensure_shipment_for_order(order: dict) -> dict | None:
    desired_status = _shipment_target_for_order_status(order.get("status"))
    if desired_status is None:
        return delivery_mock.get_shipment_by_order_id(order.get("id"))

    shipment = delivery_mock.get_shipment_by_order_id(order.get("id"))
    if shipment is None:
        address = order.get("deliveryAddress")
        if not isinstance(address, dict):
            return {
                "error": "missing_delivery_address",
                "message": "Shipment cannot be created because the order has no delivery address.",
            }
        shipment = delivery_mock.create_shipment({
            "orderId": order.get("id"),
            "carrier": order.get("deliveryMethod"),
            "deliveryType": order.get("deliveryType"),
            "address": address,
            "priceOverride": order.get("deliveryPrice"),
            "estimatedDaysOverride": order.get("estimatedDeliveryDays"),
        })
        if isinstance(shipment, dict) and shipment.get("error"):
            return shipment

    if desired_status != shipment.get("status"):
        shipment = delivery_mock.update_shipment_status(shipment["id"], desired_status)
    return shipment

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
    return jsonify(materials=UC01_inventory_management.list_materials(q))

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

@orders_bp.get("")
def list_orders():
    customer = request.args.get("customerId", type=int)
    return jsonify(
        orders=[_serialize_order(o) for o in UC07_order_processing.list_orders(customer_id=customer)],
        statuses=UC07_order_processing.list_statuses(),
        shipmentStatuses=delivery_mock.SHIPMENT_STATUSES,
    )

@orders_bp.get("/options")
def order_options():
    return jsonify(success=True, **order_mock.list_options())

@orders_bp.post("")
@require_role("Customer")
def create_order():
    data = request.get_json(silent=True) or {}
    if data.get("deliveryMethod") is not None:
        err = UC06_delivery_processing.validate(data.get("deliveryMethod"))
        if err:
            return jsonify(success=False, **err), 400
    if data.get("paymentType") is not None:
        err = UC03_payment_processing.validate(data.get("paymentType"))
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
        if not data.get("deliveryMethod"):
            data["deliveryMethod"] = delivery.get("carrier")
    order = UC02_create_order.create(data)
    response = {"success": True, "order": _serialize_order(order)}
    return jsonify(**response), 201

@orders_bp.get("/<int:oid>")
def get_order(oid: int):
    order = UC07_order_processing.get_order(oid)
    if order is None:
        return jsonify(success=False, error="not_found"), 404
    return jsonify(success=True, order=_serialize_order(order))

@orders_bp.put("/<int:oid>/status")
@require_role("Support", "Manager", "Admin")
def update_order_status(oid: int):
    data = request.get_json(silent=True) or {}
    current = UC07_order_processing.get_order(oid)
    previous_status = current.get("status") if current else None
    result = UC07_order_processing.update_status(oid, data.get("status", ""))
    if result is None:
        return jsonify(success=False, error="not_found"), 404
    if "error" in result:
        return jsonify(success=False, **result), 400
    shipment = _ensure_shipment_for_order(result)
    if isinstance(shipment, dict) and shipment.get("error"):
        if previous_status is not None:
            result["status"] = previous_status
        return jsonify(success=False, **shipment), 400
    response = {"success": True, "order": _serialize_order(result)}
    if shipment is not None:
        response["shipment"] = _serialize_shipment(shipment)
    return jsonify(**response)

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
    payload = request.get_json(silent=True) or {}
    order_id = payload.get("orderId")
    if order_id is not None:
        try:
            order = UC07_order_processing.get_order(int(order_id))
        except (TypeError, ValueError):
            order = None
        if order is not None:
            payload = {
                **payload,
                "deliveryType": order.get("deliveryType") or payload.get("deliveryType"),
                "priceOverride": order.get("deliveryPrice"),
                "estimatedDaysOverride": order.get("estimatedDeliveryDays"),
            }
    result = delivery_mock.create_shipment(payload)
    if isinstance(result, dict) and "error" in result:
        return jsonify(success=False, **result), 400
    return jsonify(success=True, shipment=_serialize_shipment(result)), 201

@delivery_bp.put("/shipments/<int:sid>/status")
@require_role("Support", "Manager", "Admin")
def update_shipment_status(sid: int):
    data = request.get_json(silent=True) or {}
    result = delivery_mock.update_shipment_status(sid, data.get("status", ""))
    if result is None:
        return jsonify(success=False, error="not_found"), 404
    if "error" in result:
        return jsonify(success=False, **result), 400
    return jsonify(success=True, shipment=_serialize_shipment(result))

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
    items = UC05_customer_request.list_requests(user.get("role"), user.get("id"))
    if items is None:
        return jsonify(success=False, error="forbidden"), 403
    return jsonify(requests=items, statuses=UC05_customer_request.request_statuses())

@support_bp.post("/requests")
@require_role("Customer")
def create_request():
    record = support_mock.create_request(request.get_json(silent=True) or {}, user=_current_user())
    return jsonify(success=True, request=record), 201

@support_bp.get("/requests/<int:rid>")
def get_request_detail(rid: int):
    record = UC05_customer_request.get_request(rid)
    if record is None:
        return jsonify(success=False, error="not_found"), 404
    if not _can_view(record, _current_user()):
        return jsonify(success=False, error="forbidden"), 403
    return jsonify(success=True, request=record)

@support_bp.patch("/requests/<int:rid>/status")
@require_role("Support", "Admin")
def patch_request_status(rid: int):
    data = request.get_json(silent=True) or {}
    result = UC05_customer_request.update_request_status(
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
    items = UC09_complaint_handling.list_complaints(user.get("role"), user.get("id"))
    if items is None:
        return jsonify(success=False, error="forbidden"), 403
    return jsonify(
        complaints=items,
        reasons=support_mock.COMPLAINT_REASONS,
        statuses=UC09_complaint_handling.complaint_statuses(),
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
    record = UC09_complaint_handling.get_complaint(cid)
    if record is None:
        return jsonify(success=False, error="not_found"), 404
    if not _can_view(record, _current_user()):
        return jsonify(success=False, error="forbidden"), 403
    return jsonify(success=True, complaint=record)

@support_bp.patch("/complaints/<int:cid>/status")
@require_role("Support", "Admin")
def patch_complaint_status(cid: int):
    data = request.get_json(silent=True) or {}
    result = UC09_complaint_handling.update_complaint_status(
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
