from flask import Flask

from . import routes


def create_app() -> Flask:
    app = Flask(__name__)

    app.register_blueprint(routes.health_bp)

    return app
