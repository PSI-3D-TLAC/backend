\
from __future__ import annotations

from flask import Flask

from . import routes

def create_app() -> Flask:
    app = Flask(__name__)

    try:
        from flask_cors import CORS                

        CORS(app, resources={r"/*": {"origins": "*"}})
    except ImportError:
                                                                            
        @app.after_request
        def _add_cors_headers(response):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-User-Role, X-User-Id"
            return response

    for blueprint in routes.ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)

    return app
