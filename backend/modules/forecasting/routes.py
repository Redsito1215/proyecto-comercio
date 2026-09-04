from flask import Blueprint, g, jsonify, request
from backend.auth.decorators import require_permission
from backend.db import get_db
from backend.modules.core.routes import validate
from backend.modules.forecasting.schemas import ForecastRunCreate
from backend.modules.forecasting.services import create_run, latest_forecasts, list_runs

forecasting_bp=Blueprint("forecasting",__name__,url_prefix="/api/v1/forecasts")

@forecasting_bp.post("/runs")
@require_permission("inventory.read")
def runs_create(): return jsonify({"data":create_run(get_db(),validate(ForecastRunCreate,request.get_json(silent=True)),g.actor_id)}),201

@forecasting_bp.get("/runs")
@require_permission("inventory.read")
def runs_list(): return jsonify({"data":list_runs(get_db())})

@forecasting_bp.get("/latest")
@require_permission("inventory.read")
def latest(): return jsonify({"data":latest_forecasts(get_db(),request.args.get("location_id","main"))})
