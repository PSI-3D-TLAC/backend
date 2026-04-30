from flask import Blueprint, jsonify, request

# NOTE: All handlers below are placeholders. They will later delegate to core
# (src/core) services. Keep return shapes stable so the frontend / clients can
# already integrate against this contract.

health_bp = Blueprint("health", __name__)
products_bp = Blueprint("products", __name__)
orders_bp = Blueprint("orders", __name__)
users_bp = Blueprint("users", __name__)


@health_bp.get("/health")
def health():
    return jsonify(status="ok")
