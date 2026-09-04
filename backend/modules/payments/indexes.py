from pymongo import ASCENDING,DESCENDING,IndexModel


def ensure_payment_indexes(db):
    db.payments.create_indexes([IndexModel("idempotency_key",unique=True),IndexModel([("sale_id",ASCENDING),("created_at",DESCENDING)])])
    db.refunds.create_indexes([IndexModel("idempotency_key",unique=True),IndexModel([("payment_id",ASCENDING),("created_at",DESCENDING)])])
