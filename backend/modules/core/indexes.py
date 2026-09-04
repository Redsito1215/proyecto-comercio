from pymongo import ASCENDING, DESCENDING, IndexModel


def ensure_indexes(db):
    barcode_index=db.products.index_information().get("barcodes_1")
    if barcode_index and "partialFilterExpression" not in barcode_index:
        db.products.drop_index("barcodes_1")
    db.categories.create_indexes([IndexModel("code", unique=True), IndexModel("name_normalized")])
    db.products.create_indexes([
        IndexModel("sku", unique=True),
        IndexModel("barcodes", unique=True, partialFilterExpression={"barcodes.0":{"$exists":True}}),
        IndexModel("name_normalized"),
    ])
    db.inventory.create_index([("product_id", ASCENDING), ("location_id", ASCENDING)], unique=True)
    db.lots.create_indexes([
        IndexModel([("product_id", ASCENDING), ("location_id", ASCENDING), ("lot_number", ASCENDING)], unique=True),
        IndexModel([("status", ASCENDING), ("expires_at", ASCENDING)]),
    ])
    db.sales.create_indexes([IndexModel("number", unique=True), IndexModel("idempotency_key", unique=True, sparse=True)])
    db.inventory_movements.create_indexes([
        IndexModel([("product_id", ASCENDING), ("occurred_at", DESCENDING)]),
        IndexModel([("source_type", ASCENDING), ("source_id", ASCENDING)]),
    ])
    db.sale_items.create_index([("sale_id", ASCENDING), ("product_id", ASCENDING)])
