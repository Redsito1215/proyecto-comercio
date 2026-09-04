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

reports_bp=Blueprint("reports",__name__,url_prefix="/api/v1/reports")

@reports_bp.get("/analytics/status")
@require_permission("inventory.read")
def analytics_health():return jsonify({"data":analytics_status()})

@reports_bp.post("/preview")
@require_permission("inventory.read")
def preview():return jsonify({"data":build_snapshot(get_db(),validate(ReportRequest,request.get_json(silent=True)))})

@reports_bp.post("/pdf")
@require_permission("inventory.read")
def pdf_create():
    db=get_db();model=validate(ReportRequest,request.get_json(silent=True));snapshot=build_snapshot(db,model);run_id=db.report_runs.insert_one({"request":model.model_dump(mode="json"),"snapshot":snapshot,"format":"pdf","actor_id":g.actor_id,"created_at":datetime.now(UTC)}).inserted_id;audit(db,g.actor_id,"report.generate","report",run_id,metadata={"sections":model.sections,"format":"pdf"});stream=create_pdf(snapshot)
    return send_file(stream,mimetype="application/pdf",as_attachment=False,download_name=f"informe-{run_id}.pdf")
