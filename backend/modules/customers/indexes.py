from pymongo import IndexModel


def ensure_customer_indexes(db):
    indexes=db.customers.index_information()
    for name in ('email_normalized_1','document_1'):
        if name in indexes and 'partialFilterExpression' not in indexes[name]:db.customers.drop_index(name)
    db.customers.create_indexes([
        IndexModel('email_normalized',unique=True,partialFilterExpression={'email_normalized':{'$type':'string'}}),
        IndexModel('document',unique=True,partialFilterExpression={'document':{'$type':'string'}}),
        IndexModel('name'),
    ])
    db.customer_consents.create_index([('customer_id',1),('purpose',1),('channel',1)],unique=True)
    db.customer_segments.create_index('customer_id',unique=True);db.churn_signals.create_index('customer_id',unique=True);db.coupons.create_index('code',unique=True)
