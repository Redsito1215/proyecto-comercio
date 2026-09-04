from pymongo import ASCENDING, DESCENDING, IndexModel


def ensure_promotion_indexes(db):
    db.promotions.create_index([("created_at",DESCENDING)])
    db.promotion_audience.create_index([("promotion_id",ASCENDING),("customer_id",ASCENDING)],unique=True)
    db.promotion_coupons.create_indexes([IndexModel("code",unique=True),IndexModel([("promotion_id",ASCENDING),("customer_id",ASCENDING)],unique=True)])
    db.promotion_redemptions.create_index([("coupon_id",ASCENDING),("sale_id",ASCENDING)],unique=True)
    db.notification_outbox.create_index([("status",ASCENDING),("created_at",ASCENDING)])
