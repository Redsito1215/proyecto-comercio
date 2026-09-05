from datetime import UTC,datetime
from pymongo import ASCENDING,DESCENDING,IndexModel

ROLE_DEFINITIONS={
    "admin":["*"],
    "cashier":["products.read","sales.read","sales.write","sales.confirm","payments.write","returns.write"],
    "supervisor":["products.read","products.write","sales.read","sales.write","sales.confirm","payments.read","payments.write","payments.refund","inventory.read","inventory.receive","inventory.count","inventory.adjust","purchases.read","purchases.write","purchases.receive","customers.read","returns.write","reports.read","catalogs.read","catalogs.write","settings.read"],
    "auditor":["products.read","sales.read","inventory.read","security.audit.read","payments.read","customers.read","reports.read"],
}


def ensure_security_indexes(db):
    db.users.create_index("email_normalized",unique=True)
    db.roles.create_index("code",unique=True)
    db.auth_sessions.create_indexes([IndexModel("token_hash",unique=True),IndexModel("expires_at",expireAfterSeconds=0)])
    db.audit_events.create_index([("occurred_at",DESCENDING),("action",ASCENDING)])
    db.settings.create_index("key",unique=True)
    now=datetime.now(UTC)
    for code,permissions in ROLE_DEFINITIONS.items():db.roles.update_one({"code":code},{"$set":{"name":code.title(),"permissions":permissions,"system":True,"updated_at":now}},upsert=True)
