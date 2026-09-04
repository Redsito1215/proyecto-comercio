from datetime import UTC,datetime
from pathlib import Path
from flask import Blueprint,g,jsonify,request,send_file
from backend.auth.decorators import require_permission
from backend.db import get_db
from backend.modules.core.routes import validate
from backend.modules.reports.pdf import create_pdf
from backend.modules.reports.schemas import ReportRequest
from backend.modules.reports.services import build_snapshot
from backend.modules.reports.analytics import analytics_status
from backend.modules.security.services import audit
from backend.common.errors import ApiError
from backend.modules.security.services import permissions_for

reports_bp=Blueprint("reports",__name__,url_prefix="/api/v1/reports")

SECTION_PERMISSIONS={"sales":"sales.read","inventory":"inventory.read","margins":"products.read","customers":"customers.read","losses":"inventory.read","payments":"payments.read","forecasts":"inventory.read"}


def authorize_sections(db,model):
    if not getattr(g,"user",None):return
    permissions=permissions_for(db,g.user)
    denied=[section for section in model.sections if "*" not in permissions and SECTION_PERMISSIONS[section] not in permissions]
    if denied:raise ApiError("No tiene permiso para todas las secciones solicitadas",403,"forbidden")

@reports_bp.get("/analytics/status")
@require_permission("reports.read")
def analytics_health():return jsonify({"data":analytics_status()})

@reports_bp.post("/preview")
@require_permission("reports.read")
def preview():
    db=get_db();model=validate(ReportRequest,request.get_json(silent=True));authorize_sections(db,model)
    return jsonify({"data":build_snapshot(db,model)})

@reports_bp.post("/pdf")
@require_permission("reports.read")
def pdf_create():
    db=get_db();model=validate(ReportRequest,request.get_json(silent=True));authorize_sections(db,model);snapshot=build_snapshot(db,model);run_id=db.report_runs.insert_one({"request":model.model_dump(mode="json"),"snapshot":snapshot,"format":"pdf","actor_id":g.actor_id,"created_at":datetime.now(UTC)}).inserted_id;audit(db,g.actor_id,"report.generate","report",run_id,metadata={"sections":model.sections,"format":"pdf"});stream=create_pdf(snapshot)
    return send_file(stream,mimetype="application/pdf",as_attachment=False,download_name=f"informe-{run_id}.pdf")
