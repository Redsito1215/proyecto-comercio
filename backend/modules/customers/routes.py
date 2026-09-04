from flask import Blueprint,g,jsonify,request
from pydantic import ValidationError
from backend.auth.decorators import require_permission
from backend.common.errors import ApiError
from backend.common.serialization import to_json
from backend.db import get_db
from backend.modules.customers.schemas import ConsentCreate,CustomerCreate
from backend.modules.customers.services import birthday_coupon,create_customer,customer_profile,recalculate_customer,record_consent

customers_bp=Blueprint('customers',__name__,url_prefix='/api/v1/customers')
def valid(model):
    try:return model.model_validate(request.get_json(silent=True) or {})
    except ValidationError as e:raise ApiError(e.errors(include_url=False)[0]['msg'],422,'validation_error') from e
@customers_bp.get('')
@require_permission('customers.read')
def listing():
    q=request.args.get('q','');criteria={'status':'active'}
    if q:criteria['$or']=[{'name':{'$regex':q,'$options':'i'}},{'email_normalized':{'$regex':q.lower(),'$options':'i'}},{'document':q}]
    rows=[]
    for x in get_db().customers.find(criteria).sort('name',1).limit(100):x=to_json(x);x['id']=x.pop('_id');rows.append(x)
    return jsonify({'data':rows})
@customers_bp.post('')
@require_permission('customers.write')
def create():return jsonify({'data':create_customer(get_db(),valid(CustomerCreate),g.actor_id)}),201
@customers_bp.get('/<cid>')
@require_permission('customers.read')
def profile(cid):return jsonify({'data':customer_profile(get_db(),cid)})
@customers_bp.post('/<cid>/consents')
@require_permission('customers.write')
def consent(cid):return jsonify({'data':record_consent(get_db(),cid,valid(ConsentCreate),g.actor_id)}),201
@customers_bp.post('/<cid>/recalculate')
@require_permission('customers.analyze')
def recalc(cid):return jsonify({'data':recalculate_customer(get_db(),cid)})
@customers_bp.post('/<cid>/birthday-coupon')
@require_permission('customers.promote')
def coupon(cid):return jsonify({'data':birthday_coupon(get_db(),cid,g.actor_id)}),201
