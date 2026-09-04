from flask import Blueprint,g,jsonify,request
from backend.auth.decorators import require_permission
from backend.common.errors import ApiError
from backend.db import get_db
from backend.modules.core.routes import validate
from backend.modules.controls.schemas import AlertResolve,CashClose,CashCountCreate,CashMovementCreate,CashSessionOpen,LossCreate
from backend.modules.controls.services import add_movement,dashboard,list_alerts,open_session,record_count,record_loss,resolve_alert

controls_bp=Blueprint("controls",__name__,url_prefix="/api/v1/controls")

@controls_bp.get("/dashboard")
@require_permission("inventory.read")
def controls_dashboard():return jsonify({"data":dashboard(get_db())})

@controls_bp.post("/cash-sessions")
@require_permission("sales.write")
def sessions_open():return jsonify({"data":open_session(get_db(),validate(CashSessionOpen,request.get_json(silent=True)),g.actor_id)}),201

@controls_bp.post("/cash-sessions/<session_id>/movements")
@require_permission("sales.write")
def movement_create(session_id):
    key=request.headers.get("Idempotency-Key","").strip()
    if not key:raise ApiError("Se requiere Idempotency-Key",400,"idempotency_key_required")
    return jsonify({"data":add_movement(get_db(),session_id,validate(CashMovementCreate,request.get_json(silent=True)),key,g.actor_id)}),201

@controls_bp.post("/cash-sessions/<session_id>/counts")
@require_permission("inventory.adjust")
def count_create(session_id):return jsonify({"data":record_count(get_db(),session_id,validate(CashCountCreate,request.get_json(silent=True)),g.actor_id)}),201

@controls_bp.post("/cash-sessions/<session_id>/close")
@require_permission("inventory.adjust")
def session_close(session_id):return jsonify({"data":record_count(get_db(),session_id,validate(CashClose,request.get_json(silent=True)),g.actor_id,True)})

@controls_bp.post("/losses")
@require_permission("inventory.adjust")
def loss_create():return jsonify({"data":record_loss(get_db(),validate(LossCreate,request.get_json(silent=True)),g.actor_id)}),201

@controls_bp.get("/alerts")
@require_permission("inventory.read")
def alerts_list():return jsonify({"data":list_alerts(get_db())})

@controls_bp.post("/alerts/<alert_id>/resolve")
@require_permission("inventory.adjust")
def alert_resolve(alert_id):return jsonify({"data":resolve_alert(get_db(),alert_id,validate(AlertResolve,request.get_json(silent=True)),g.actor_id)})
