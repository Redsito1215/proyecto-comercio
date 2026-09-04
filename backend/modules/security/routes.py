from flask import Blueprint,g,jsonify,request
from backend.auth.decorators import require_permission
from backend.common.errors import ApiError
from backend.db import get_db
from backend.modules.core.routes import validate
from backend.modules.security.schemas import BootstrapCreate,LoginCreate,UserCreate
from backend.modules.security.services import audit_log,bootstrap,create_user,login,logout

security_bp=Blueprint("security",__name__,url_prefix="/api/v1/security")

@security_bp.post("/bootstrap")
def bootstrap_create():return jsonify({"data":bootstrap(get_db(),validate(BootstrapCreate,request.get_json(silent=True)))}),201

@security_bp.post("/login")
def login_create():return jsonify({"data":login(get_db(),validate(LoginCreate,request.get_json(silent=True)))})

@security_bp.post("/logout")
@require_permission("authenticated")
def logout_create():
    raw=request.headers.get("Authorization","").removeprefix("Bearer ").strip()
    if not raw:raise ApiError("Sesión requerida",401,"authentication_required")
    return jsonify({"data":logout(get_db(),raw,g.actor_id)})

@security_bp.post("/users")
@require_permission("security.users.write")
def users_create():return jsonify({"data":create_user(get_db(),validate(UserCreate,request.get_json(silent=True)),g.actor_id)}),201

@security_bp.get("/audit")
@require_permission("security.audit.read")
def audit_list():return jsonify({"data":audit_log(get_db())})
