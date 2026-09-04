from flask import Blueprint,g,jsonify,request
from backend.auth.decorators import require_permission
from backend.db import get_db
from backend.modules.core.routes import validate
from backend.modules.promotions.schemas import PromotionCreate,RedemptionCreate
from backend.modules.promotions.services import activate,create_promotion,list_promotions,metrics,prepare_audience,redeem

promotions_bp=Blueprint("promotions",__name__,url_prefix="/api/v1/promotions")

@promotions_bp.get("")
@require_permission("products.read")
def promotions_list():return jsonify({"data":list_promotions(get_db())})

@promotions_bp.post("")
@require_permission("products.write")
def promotions_create():return jsonify({"data":create_promotion(get_db(),validate(PromotionCreate,request.get_json(silent=True)),g.actor_id)}),201

@promotions_bp.post("/<promotion_id>/audience")
@require_permission("products.write")
def audience_create(promotion_id):return jsonify({"data":prepare_audience(get_db(),promotion_id)})

@promotions_bp.post("/<promotion_id>/activate")
@require_permission("products.write")
def promotion_activate(promotion_id):return jsonify({"data":activate(get_db(),promotion_id,g.actor_id)})

@promotions_bp.get("/<promotion_id>/metrics")
@require_permission("products.read")
def promotion_metrics(promotion_id):return jsonify({"data":metrics(get_db(),promotion_id)})

@promotions_bp.post("/redemptions")
@require_permission("sales.write")
def redemption_create():return jsonify({"data":redeem(get_db(),validate(RedemptionCreate,request.get_json(silent=True)),g.actor_id)}),201
