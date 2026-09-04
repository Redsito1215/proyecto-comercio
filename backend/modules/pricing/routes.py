from flask import Blueprint, g, jsonify, request
from backend.auth.decorators import require_permission
from backend.db import get_db
from backend.modules.core.routes import validate
from backend.modules.pricing.schemas import CompetitorPriceCreate, PriceChange, PriceSimulation
from backend.modules.pricing.services import apply_price, list_margins, market_comparison, record_competitor_price, simulate_price

pricing_bp = Blueprint("pricing", __name__, url_prefix="/api/v1/pricing")

@pricing_bp.get("/margins")
@require_permission("products.read")
def margins(): return jsonify({"data": list_margins(get_db())})

@pricing_bp.post("/simulations")
@require_permission("products.read")
def simulations(): return jsonify({"data": simulate_price(get_db(), validate(PriceSimulation, request.get_json(silent=True)))})

@pricing_bp.put("/products/<product_id>/price")
@require_permission("products.write")
def price_update(product_id): return jsonify({"data": apply_price(get_db(), product_id, validate(PriceChange, request.get_json(silent=True)), g.actor_id)})

@pricing_bp.post("/competitor-prices")
@require_permission("products.write")
def competitor_create(): return jsonify({"data": record_competitor_price(get_db(), validate(CompetitorPriceCreate, request.get_json(silent=True)), g.actor_id)}), 201

@pricing_bp.get("/products/<product_id>/market-comparison")
@require_permission("products.read")
def comparison(product_id): return jsonify({"data": market_comparison(get_db(), product_id)})
