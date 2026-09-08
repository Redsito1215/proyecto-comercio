from flask import Blueprint,g,jsonify,request,send_file
from backend.auth.decorators import require_permission
from backend.common.errors import ApiError
from backend.db import get_db
from backend.modules.core.routes import validate
from backend.modules.payments.schemas import PaymentCreate,RefundCreate
from backend.modules.payments.pdf import create_receipt_pdf
from backend.modules.payments.services import create_payment,list_payable_sales,list_payments,receipt_data,refund_payment

payments_bp=Blueprint("payments",__name__,url_prefix="/api/v1/payments")

def key_required():
    key=request.headers.get("Idempotency-Key","").strip()
    if not key:raise ApiError("Se requiere Idempotency-Key",400,"idempotency_key_required")
    return key

@payments_bp.get("")
@require_permission("payments.read")
def payments_list():return jsonify({"data":list_payments(get_db())})

@payments_bp.get("/pending-sales")
@require_permission("payments.write")
def pending_sales_list():return jsonify({"data":list_payable_sales(get_db())})

@payments_bp.post("")
@require_permission("payments.write")
def payment_create():
    key=key_required()
    return jsonify({"data":create_payment(get_db(),validate(PaymentCreate,request.get_json(silent=True)),key,g.actor_id)}),201

@payments_bp.get("/<payment_id>/receipt.pdf")
@require_permission("payments.write")
def payment_receipt(payment_id):
    data=receipt_data(get_db(),payment_id)
    return send_file(create_receipt_pdf(data),mimetype="application/pdf",as_attachment=False,download_name=f'comprobante-{data["sale_number"]}.pdf')

@payments_bp.post("/<payment_id>/refunds")
@require_permission("payments.refund")
def refund_create(payment_id):
    key=key_required()
    return jsonify({"data":refund_payment(get_db(),payment_id,validate(RefundCreate,request.get_json(silent=True)),key,g.actor_id)}),201
