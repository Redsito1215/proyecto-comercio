from pymongo import IndexModel
def ensure_customer_indexes(db):
    db.customers.create_indexes([IndexModel('email_normalized',unique=True,sparse=True),IndexModel('document',unique=True,sparse=True),IndexModel('name')])
    db.customer_consents.create_index([('customer_id',1),('purpose',1),('channel',1)],unique=True)
    db.customer_segments.create_index('customer_id',unique=True);db.churn_signals.create_index('customer_id',unique=True);db.coupons.create_index('code',unique=True)
