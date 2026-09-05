import hashlib,secrets
from datetime import UTC,datetime,timedelta
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash,generate_password_hash

from backend.common.errors import ApiError
from backend.common.serialization import to_json

LOCK_ATTEMPTS=5


def audit(db,actor,action,entity_type,entity_id=None,outcome="success",metadata=None):
    safe={k:v for k,v in (metadata or {}).items() if k.lower() not in {"password","token","pan","cvv","card_number"}}
    db.audit_events.insert_one({"actor_id":str(actor) if actor else "anonymous","action":action,"entity_type":entity_type,"entity_id":str(entity_id) if entity_id else None,"outcome":outcome,"metadata":safe,"occurred_at":datetime.now(UTC)})


def _create_user(db,model,roles):
    now=datetime.now(UTC);doc={"name":model.name.strip(),"email":str(model.email),"email_normalized":str(model.email).lower(),"password_hash":generate_password_hash(model.password,method="scrypt"),"roles":roles,"status":"active","failed_attempts":0,"locked_until":None,"created_at":now,"updated_at":now}
    try:uid=db.users.insert_one(doc).inserted_id
    except DuplicateKeyError as error:raise ApiError("El correo ya está registrado",409,"duplicate_user") from error
    return uid


def bootstrap(db,model):
    if db.users.count_documents({"roles":"admin"})>0:raise ApiError("La inicialización ya fue realizada",409,"bootstrap_closed")
    try:db.bootstrap_state.insert_one({"_id":"admin-bootstrap","claimed_at":datetime.now(UTC)})
    except DuplicateKeyError as error:raise ApiError("La inicialización ya fue realizada",409,"bootstrap_closed") from error
    try:uid=_create_user(db,model,["admin"])
    except Exception:
        db.bootstrap_state.delete_one({"_id":"admin-bootstrap"});raise
    audit(db,uid,"security.bootstrap","user",uid)
    return {"id":str(uid),"name":model.name,"email":str(model.email),"roles":["admin"]}


def bootstrap_available(db):
    return db.users.count_documents({"roles":"admin"})==0 and db.bootstrap_state.count_documents({"_id":"admin-bootstrap"})==0


def create_user(db,model,actor):
    known={x["code"] for x in db.roles.find({"code":{"$in":model.roles}})}
    if known!=set(model.roles):raise ApiError("Rol desconocido",422,"unknown_role")
    uid=_create_user(db,model,model.roles);audit(db,actor,"user.create","user",uid,metadata={"roles":model.roles})
    return {"id":str(uid),"name":model.name,"email":str(model.email),"roles":model.roles}


def login(db,model):
    now=datetime.now(UTC);email=str(model.email).lower();user=db.users.find_one({"email_normalized":email,"status":"active"})
    if user and user.get("locked_until"):
        locked=user["locked_until"];compare=now.replace(tzinfo=None) if locked.tzinfo is None else now
        if locked>compare:audit(db,user["_id"],"auth.login","user",user["_id"],"blocked");raise ApiError("Cuenta temporalmente bloqueada",423,"account_locked")
    if not user or not check_password_hash(user["password_hash"],model.password):
        if user:
            attempts=user.get("failed_attempts",0)+1;update={"failed_attempts":attempts}
            if attempts>=LOCK_ATTEMPTS:update["locked_until"]=now+timedelta(minutes=15)
            db.users.update_one({"_id":user["_id"]},{"$set":update});audit(db,user["_id"],"auth.login","user",user["_id"],"failure")
        raise ApiError("Credenciales inválidas",401,"invalid_credentials")
    raw=secrets.token_urlsafe(48);token_hash=hashlib.sha256(raw.encode()).hexdigest();expires=now+timedelta(hours=8)
    db.auth_sessions.insert_one({"user_id":user["_id"],"token_hash":token_hash,"expires_at":expires,"created_at":now,"revoked_at":None})
    db.users.update_one({"_id":user["_id"]},{"$set":{"failed_attempts":0,"locked_until":None,"last_login_at":now}});audit(db,user["_id"],"auth.login","user",user["_id"])
    return {"access_token":raw,"token_type":"Bearer","expires_at":expires.isoformat(),"user":{"id":str(user["_id"]),"name":user["name"],"roles":user["roles"]}}


def authenticate(db,raw_token):
    if not raw_token:return None
    token_hash=hashlib.sha256(raw_token.encode()).hexdigest();now=datetime.now(UTC)
    session=db.auth_sessions.find_one({"token_hash":token_hash,"revoked_at":None,"expires_at":{"$gt":now}})
    if not session:return None
    user=db.users.find_one({"_id":session["user_id"],"status":"active"})
    return user


def permissions_for(db,user):
    permissions=set()
    for role in db.roles.find({"code":{"$in":user.get("roles",[])}}):permissions.update(role["permissions"])
    return permissions


def logout(db,raw_token,actor):
    token_hash=hashlib.sha256(raw_token.encode()).hexdigest();db.auth_sessions.update_one({"token_hash":token_hash,"revoked_at":None},{"$set":{"revoked_at":datetime.now(UTC)}});audit(db,actor,"auth.logout","session")
    return {"status":"revoked"}


def audit_log(db,action="",outcome="",actor="",date_from=None,date_to=None):
    query={}
    if action:query["action"]={"$regex":action,"$options":"i"}
    if outcome:query["outcome"]=outcome
    if actor:query["actor_id"]={"$regex":actor,"$options":"i"}
    dates={}
    if date_from:dates["$gte"]=date_from
    if date_to:dates["$lte"]=date_to
    if dates:query["occurred_at"]=dates
    return [to_json({**x,"id":str(x["_id"])}) for x in db.audit_events.find(query).sort("occurred_at",-1).limit(1000)]


def list_users(db):
    return [to_json({"id":str(x["_id"]),"name":x["name"],"email":x["email"],"roles":x.get("roles",[]),"status":x.get("status","active"),"last_login_at":x.get("last_login_at")}) for x in db.users.find({}, {"password_hash":0}).sort("name",1)]


def list_roles(db):
    return [to_json({**x,"id":str(x["_id"])}) for x in db.roles.find().sort("name",1)]


def create_role(db,model,actor):
    permissions=sorted(set(model.permissions))
    if "*" in permissions:raise ApiError("El permiso total está reservado para el rol administrador",422,"reserved_permission")
    doc={"code":model.code,"name":model.name.strip(),"permissions":permissions,"system":False,"created_at":datetime.now(UTC),"updated_at":datetime.now(UTC)}
    try:identifier=db.roles.insert_one(doc).inserted_id
    except DuplicateKeyError as error:raise ApiError("El código del rol ya existe",409,"duplicate_role") from error
    audit(db,actor,"role.create","role",identifier,metadata={"code":model.code,"permissions":permissions})
    return to_json({**doc,"id":str(identifier)})


def business_settings(db):
    defaults={"business_name":"Comercio Inteligente","tax_id":"","currency":"USD","timezone":"America/Guayaquil","low_stock_threshold":5,"expiry_warning_days":30}
    stored=db.settings.find_one({"key":"business"},{"_id":0,"key":0}) or {}
    return {**defaults,**stored}


def update_business_settings(db,model,actor):
    values=model.model_dump();values["updated_at"]=datetime.now(UTC);values["updated_by"]=str(actor)
    db.settings.update_one({"key":"business"},{"$set":values,"$setOnInsert":{"created_at":datetime.now(UTC)}},upsert=True)
    audit(db,actor,"settings.update","business",metadata={"fields":list(type(model).model_fields)})
    return to_json(values)
