from pymongo import ASCENDING,DESCENDING,IndexModel


def ensure_control_indexes(db):
    db.cash_sessions.create_index([("register_id",ASCENDING)],unique=True,partialFilterExpression={"status":"open"},name="one_open_session_per_register")
    db.cash_movements.create_indexes([IndexModel("idempotency_key",unique=True,sparse=True),IndexModel([("session_id",ASCENDING),("occurred_at",ASCENDING)])])
    db.cash_counts.create_index([("session_id",ASCENDING),("counted_at",DESCENDING)])
    db.loss_events.create_index([("occurred_at",DESCENDING),("type",ASCENDING)])
    db.risk_alerts.create_index([("status",ASCENDING),("severity",ASCENDING),("created_at",DESCENDING)])
