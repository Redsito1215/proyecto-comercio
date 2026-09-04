from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from backend.common.errors import register_error_handlers
from backend.config import get_settings
from backend.db import get_db, ping
from backend.modules.core.indexes import ensure_indexes


def create_app(testing: bool = False) -> Flask:
    frontend = Path(__file__).resolve().parents[1] / "frontend"
    app = Flask(__name__, static_folder=str(frontend), static_url_path="")
    app.config.update(TESTING=testing, SECRET_KEY=get_settings().flask_secret_key)
    register_error_handlers(app)

    @app.get("/api/v1/health")
    def health():
        return jsonify({"status": "ok", "mongo": ping()})

    @app.get("/")
    def index():
        return send_from_directory(frontend, "index.html")

    if not testing:
        ensure_indexes(get_db())
    return app


if __name__ == "__main__":
    settings = get_settings()
    create_app().run(host=settings.app_host, port=settings.app_port)
