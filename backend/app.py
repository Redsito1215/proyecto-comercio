from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from backend.common.errors import register_error_handlers
from backend.config import get_settings
from backend.db import get_db, ping
from backend.modules.core.indexes import ensure_indexes
from backend.modules.core.routes import core_bp
from backend.modules.customers.indexes import ensure_customer_indexes
from backend.modules.customers.routes import customers_bp
from backend.modules.pricing.indexes import ensure_pricing_indexes
from backend.modules.pricing.routes import pricing_bp
from backend.modules.forecasting.indexes import ensure_forecast_indexes
from backend.modules.forecasting.routes import forecasting_bp


def create_app(testing: bool = False) -> Flask:
    frontend = Path(__file__).resolve().parents[1] / "frontend"
    app = Flask(__name__, static_folder=str(frontend), static_url_path="")
    app.config.update(TESTING=testing, SECRET_KEY=get_settings().flask_secret_key)
    register_error_handlers(app)
    app.register_blueprint(core_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(pricing_bp)
    app.register_blueprint(forecasting_bp)

    @app.get("/api/v1/health")
    def health():
        return jsonify({"status": "ok", "mongo": ping()})

    @app.get("/")
    def index():
        return send_from_directory(frontend, "index.html")

    if not testing:
        ensure_indexes(get_db())
        ensure_customer_indexes(get_db())
        ensure_pricing_indexes(get_db())
        ensure_forecast_indexes(get_db())
    return app


if __name__ == "__main__":
    settings = get_settings()
    create_app().run(host=settings.app_host, port=settings.app_port)
