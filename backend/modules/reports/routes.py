from datetime import UTC,datetime
from flask import Blueprint,g,jsonify,request,send_file
from backend.auth.decorators import require_permission
from backend.db import get_db
from backend.modules.core.routes import validate
from backend.modules.reports.catalog import SIMPLE_BY_ID,SIMPLE_REPORTS,describe as describe_simple
from backend.modules.reports.compuestos import COMPLEX_BY_ID,COMPLEX_REPORTS,describe as describe_complex,run_complex
from backend.modules.reports.pdf import create_pdf,create_report_pdf
from backend.modules.reports.schemas import ReportQuery,ReportRequest
from backend.modules.reports.services import build_snapshot
from backend.modules.reports.simple import run_simple
from backend.modules.reports.analytics import analytics_status
from backend.modules.reports.warehouse import WarehouseUnavailable
from backend.modules.security.services import audit,permissions_for
from backend.common.errors import ApiError

reports_bp=Blueprint("reports",__name__,url_prefix="/api/v1/reports")

SECTION_PERMISSIONS={"sales":"sales.read","inventory":"inventory.read","margins":"products.read","customers":"customers.read","losses":"inventory.read","payments":"payments.read","forecasts":"inventory.read"}


def actor_permissions(db):
    """Permisos del solicitante, o None cuando corre el bypass de pruebas."""
    return permissions_for(db,g.user) if getattr(g,"user",None) else None


def grants(permissions,required):
    return permissions is None or "*" in permissions or required in permissions


def authorize_sections(db,model):
    permissions=actor_permissions(db)
    if permissions is None:return
    denied=[section for section in model.sections if not grants(permissions,SECTION_PERMISSIONS[section])]
    if denied:raise ApiError("No tiene permiso para todas las secciones solicitadas",403,"forbidden")


def find_report(index,report_id):
    report=index.get(report_id.upper())
    if not report:raise ApiError("Informe no encontrado",404,"report_not_found")
    return report


def authorize_report(db,report):
    if not grants(actor_permissions(db),report["permission"]):raise ApiError("No tiene permiso para este informe",403,"forbidden")


def execute(db,report_id,complex_report):
    """Valida filtros, autoriza y ejecuta; traduce la caída del almacén en 503."""
    report=find_report(COMPLEX_BY_ID if complex_report else SIMPLE_BY_ID,report_id)
    authorize_report(db,report)
    params=validate(ReportQuery,request.args.to_dict())
    try:
        return run_complex(report["id"],params) if complex_report else run_simple(db,report["id"],params)
    except WarehouseUnavailable as error:
        raise ApiError(f"El almacén analítico no está disponible: {error}",503,"warehouse_unavailable") from error


def record_export(db,report,rows):
    db.report_exports.insert_one({"report_id":report["id"],"report_type":report["tipo"],"format":"pdf","row_count":rows,"actor_id":getattr(g,"actor_id",None),"created_at":datetime.now(UTC)})
    audit(db,getattr(g,"actor_id",None),"report.export","report",report["id"],metadata={"tipo":report["tipo"],"format":"pdf","rows":rows})


@reports_bp.get("/analytics/status")
@require_permission("reports.read")
def analytics_health():return jsonify({"data":analytics_status()})


@reports_bp.get("/catalog")
@require_permission("reports.read")
def catalog():
    """Catálogo filtrado por los permisos de quien pregunta."""
    permissions=actor_permissions(get_db());kind=(request.args.get("tipo") or "all").lower()
    simple=[describe_simple(x) for x in SIMPLE_REPORTS if grants(permissions,x["permission"])]
    complex_reports=[describe_complex(x) for x in COMPLEX_REPORTS if grants(permissions,x["permission"])]
    data={"simples":simple if kind in ("all","simple") else [],"compuestos":complex_reports if kind in ("all","compuesto") else []}
    return jsonify({"data":{**data,"total":len(data["simples"])+len(data["compuestos"])}})


@reports_bp.get("/simple/<report_id>")
@require_permission("reports.read")
def run_simple_report(report_id):
    result=execute(get_db(),report_id,complex_report=False)
    return jsonify({"data":{**result,"generated_at":datetime.now(UTC).isoformat()}})


@reports_bp.get("/compuestos/<report_id>")
@require_permission("reports.read")
def run_complex_report(report_id):
    result=execute(get_db(),report_id,complex_report=True)
    return jsonify({"data":{**result,"generated_at":datetime.now(UTC).isoformat()}})


@reports_bp.get("/simple/<report_id>/pdf")
@require_permission("reports.read")
def simple_pdf(report_id):
    db=get_db();result=execute(db,report_id,complex_report=False);record_export(db,result["report"],result["total"])
    stream=create_report_pdf(result["report"],result["rows"],datetime.now(UTC).isoformat())
    return send_file(stream,mimetype="application/pdf",as_attachment=False,download_name=f'{result["report"]["id"]}.pdf')


@reports_bp.get("/compuestos/<report_id>/pdf")
@require_permission("reports.read")
def complex_pdf(report_id):
    db=get_db();result=execute(db,report_id,complex_report=True);record_export(db,result["report"],result["total"])
    stream=create_report_pdf(result["report"],result["rows"],datetime.now(UTC).isoformat())
    return send_file(stream,mimetype="application/pdf",as_attachment=False,download_name=f'{result["report"]["id"]}.pdf')


@reports_bp.get("/exports")
@require_permission("security.audit.read")
def export_history():
    rows=list(get_db().report_exports.find({},{"_id":0}).sort("created_at",-1).limit(100))
    return jsonify({"data":{"exports":[{**x,"created_at":x["created_at"].isoformat()} for x in rows],"total":len(rows)}})


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
