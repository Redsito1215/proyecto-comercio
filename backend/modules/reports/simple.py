"""Ejecución de los informes simples del catálogo contra MongoDB.

Cada ejecutor devuelve una lista de filas alineada, posición a posición, con las
columnas declaradas en ``catalog.py``. El test ``test_reports_catalog`` comprueba
esa alineación para todo el catálogo, así que al añadir un informe basta con
mantener la misma longitud en ambos sitios.
"""
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal

from bson import Decimal128, ObjectId

from backend.common.serialization import to_json
from backend.modules.reports.catalog import SIMPLE_BY_ID, check_width


def dec(value):
    return value.to_decimal() if isinstance(value, Decimal128) else Decimal(str(value or 0))


def money(value):
    return str(dec(value))


def moment(value):
    return to_json(value)[:19].replace("T", " ") if value else "-"


def date_range(query, field, params):
    if params.date_from: query.setdefault(field, {})["$gte"] = datetime.combine(params.date_from, time.min, UTC)
    if params.date_to: query.setdefault(field, {})["$lte"] = datetime.combine(params.date_to, time.max, UTC)
    return query


def matches(params, *values):
    """Filtro de texto aplicado en memoria sobre las columnas ya resueltas.

    Las filas se buscan por nombre de producto o cliente, datos que viven en otra
    colección y no en el documento consultado, así que un filtro en Mongo exigiría
    un ``$lookup`` por informe. Con el tope de ``limit`` filas la comparación
    directa es suficiente y mantiene cada ejecutor legible.
    """
    if not params.search: return True
    needle = params.search.lower()
    return any(needle in str(value).lower() for value in values if value is not None)


class ProductCache:
    """Resuelve product_id → documento una sola vez por ejecución del informe."""

    def __init__(self, db):
        self.db, self.cache = db, {}

    def get(self, product_id):
        if product_id not in self.cache:
            self.cache[product_id] = self.db.products.find_one({"_id": product_id}) or {}
        return self.cache[product_id]

    def labels(self, product_id):
        product = self.get(product_id)
        return product.get("sku", "-"), product.get("name", "Producto")


def rs01(db, params):
    query = date_range({"status": {"$in": ["confirmed", "partially_returned"]}}, "confirmed_at", params)
    rows = []
    for sale in db.sales.find(query).sort("confirmed_at", -1).limit(params.limit):
        customer = db.customers.find_one({"_id": sale["customer_id"]}) if isinstance(sale.get("customer_id"), ObjectId) else None
        name = customer["name"] if customer else "Consumidor final"
        if not matches(params, sale.get("number"), name): continue
        rows.append([sale.get("number", "-"), moment(sale.get("confirmed_at")), sale.get("location_id", "main"),
                     sale["status"], name, money(sale.get("total"))])
    return rows


def rs02(db, params):
    products = ProductCache(db)
    rows = []
    for stock in db.inventory.find({"available": {"$lte": params.threshold}}).sort("available", 1).limit(params.limit):
        sku, name = products.labels(stock["product_id"])
        if not matches(params, sku, name): continue
        rows.append([sku, name, stock.get("location_id", "main"), stock.get("available", 0),
                     stock.get("reserved", 0), money(stock.get("average_cost"))])
    return rows


def rs03(db, params):
    now = datetime.now(UTC)
    limit_date = now + timedelta(days=params.days)
    products = ProductCache(db)
    rows = []
    for lot in db.lots.find({"status": "available", "available_quantity": {"$gt": 0},
                             "expires_at": {"$ne": None, "$lte": limit_date}}).sort("expires_at", 1).limit(params.limit):
        sku, name = products.labels(lot["product_id"])
        if not matches(params, sku, name, lot.get("lot_number")): continue
        expires = lot["expires_at"]
        remaining = (expires.replace(tzinfo=UTC) - now).days if expires.tzinfo is None else (expires - now).days
        rows.append([lot.get("lot_number", "-"), sku, name, lot.get("location_id", "main"),
                     lot.get("available_quantity", 0), moment(expires), remaining])
    return rows


def rs04(db, params):
    products = ProductCache(db)
    rows = []
    for movement in db.inventory_movements.find(date_range({}, "occurred_at", params)).sort("occurred_at", -1).limit(params.limit):
        sku, name = products.labels(movement["product_id"])
        if not matches(params, sku, name, movement.get("type")): continue
        rows.append([moment(movement.get("occurred_at")), sku, name, movement.get("location_id", "main"),
                     movement.get("type", "-"), movement.get("quantity", 0),
                     money(movement.get("unit_cost")), movement.get("source_type", "-")])
    return rows


def rs05(db, params):
    query = date_range({"status": {"$in": ["sent", "partially_received"]}}, "created_at", params)
    rows = []
    for order in db.purchase_orders.find(query).sort("created_at", -1).limit(params.limit):
        if not matches(params, order.get("number"), order.get("supplier_name")): continue
        pending = db.purchase_order_items.count_documents({"purchase_order_id": order["_id"], "pending_quantity": {"$gt": 0}})
        rows.append([order.get("number", "-"), order.get("supplier_name", "-"), order.get("location_id", "main"),
                     order["status"], money(order.get("total")), pending, moment(order.get("created_at"))])
    return rows


def rs06(db, params):
    products = ProductCache(db)
    rows = []
    for lost in db.lost_sales.find(date_range({}, "occurred_at", params)).sort("occurred_at", -1).limit(params.limit):
        sku, name = products.labels(lost["product_id"])
        if not matches(params, sku, name, lost.get("reason")): continue
        rows.append([moment(lost.get("occurred_at")), sku, name, lost.get("requested_quantity", 0), lost.get("reason", "-")])
    return rows


def rs07(db, params):
    rows = []
    for customer in db.customers.find({"status": "active"}).sort("name", 1).limit(params.limit):
        if not matches(params, customer.get("name"), customer.get("email")): continue
        segment = db.customer_segments.find_one({"customer_id": customer["_id"]}) or {}
        rows.append([customer["name"], customer.get("email", "-"), segment.get("segment", "sin_historial"),
                     segment.get("frequency", 0), money(segment.get("spend")), money(segment.get("margin")),
                     segment.get("explanation", "Sin cálculo")])
    return rows


def rs08(db, params):
    rows = []
    for signal in db.churn_signals.find().limit(params.limit):
        customer = db.customers.find_one({"_id": signal["customer_id"]}) or {}
        name = customer.get("name", "Cliente")
        if not matches(params, name, signal.get("status")): continue
        rows.append([name, signal.get("status", "-"), signal.get("expected_interval_days", "-"),
                     signal.get("days_since_purchase", "-"), signal.get("delay_days", "-"),
                     signal.get("confidence", 0), signal.get("reason", "-")])
    return rows


def rs09(db, params):
    rows = []
    for consent in db.customer_consents.find().sort("updated_at", -1).limit(params.limit):
        customer = db.customers.find_one({"_id": consent["customer_id"]}) or {}
        name = customer.get("name", "Cliente")
        if not matches(params, name, consent.get("purpose"), consent.get("channel")): continue
        rows.append([name, consent.get("purpose", "-"), consent.get("channel", "-"), consent.get("status", "-"),
                     consent.get("source", "-"), moment(consent.get("updated_at"))])
    return rows


def rs10(db, params):
    products = ProductCache(db)
    rows = []
    for change in db.price_changes.find(date_range({}, "effective_at", params)).sort("effective_at", -1).limit(params.limit):
        sku, name = products.labels(change["product_id"])
        if not matches(params, sku, name, change.get("reason")): continue
        rows.append([moment(change.get("effective_at")), sku, name, money(change.get("old_price")),
                     money(change.get("new_price")), money(change.get("margin_percent")), change.get("reason", "-")])
    return rows


def rs11(db, params):
    products = ProductCache(db)
    rows = []
    for observation in db.competitor_prices.find(date_range({}, "observed_at", params)).sort("observed_at", -1).limit(params.limit):
        sku, name = products.labels(observation["product_id"])
        if not matches(params, sku, name, observation.get("competitor")): continue
        rows.append([moment(observation.get("observed_at")), sku, name, observation.get("competitor", "-"),
                     observation.get("channel", "-"), money(observation.get("observed_price")), observation.get("source", "-")])
    return rows


def rs12(db, params):
    run = db.forecast_runs.find_one({"status": "completed"}, sort=[("created_at", -1)])
    if not run: return []
    rows = []
    for forecast in db.forecasts.find({"run_id": run["_id"]}).sort("recommended_quantity", -1).limit(params.limit):
        if not matches(params, forecast.get("sku"), forecast.get("product_name")): continue
        rows.append([forecast.get("sku", "-"), forecast.get("product_name", "Producto"), forecast.get("expected_units", 0),
                     f'{forecast.get("lower_bound", 0)}-{forecast.get("upper_bound", 0)}', forecast.get("confidence", "-"),
                     forecast.get("available", 0), forecast.get("recommended_quantity", 0)])
    return rows


def rs13(db, params):
    rows = []
    for promotion in db.promotions.find(date_range({}, "created_at", params)).sort("created_at", -1).limit(params.limit):
        if not matches(params, promotion.get("name"), promotion.get("segment"), promotion.get("status")): continue
        rows.append([promotion.get("name", "-"), promotion.get("segment", "all"), promotion.get("channel", "-"),
                     money(promotion.get("discount_percent")), promotion.get("status", "-"),
                     moment(promotion.get("valid_from")), moment(promotion.get("valid_until"))])
    return rows


def rs14(db, params):
    rows = []
    for coupon in db.promotion_coupons.find().sort("created_at", -1).limit(params.limit):
        customer = db.customers.find_one({"_id": coupon["customer_id"]}) or {}
        name = customer.get("name", "Cliente")
        if not matches(params, coupon.get("code"), name): continue
        rows.append([coupon.get("code", "-"), name, coupon.get("status", "-"), coupon.get("usage_count", 0),
                     coupon.get("usage_limit", 0), moment(coupon.get("valid_from")), moment(coupon.get("valid_until"))])
    return rows


def rs15(db, params):
    rows = []
    for session in db.cash_sessions.find(date_range({}, "opened_at", params)).sort("opened_at", -1).limit(params.limit):
        difference = session.get("difference")
        rows.append([session.get("register_id", "-"), session.get("location_id", "main"), session.get("status", "-"),
                     money(session.get("opening_amount")),
                     money(session["expected_balance"]) if session.get("expected_balance") is not None else "-",
                     money(session["counted_balance"]) if session.get("counted_balance") is not None else "-",
                     money(difference) if difference is not None else "-", moment(session.get("opened_at"))])
    return rows


def rs16(db, params):
    products = ProductCache(db)
    rows = []
    for loss in db.loss_events.find(date_range({}, "occurred_at", params)).sort("occurred_at", -1).limit(params.limit):
        sku, name = products.labels(loss["product_id"])
        if not matches(params, sku, name, loss.get("type"), loss.get("reason")): continue
        rows.append([moment(loss.get("occurred_at")), sku, name, loss.get("location_id", "main"), loss.get("type", "-"),
                     loss.get("quantity", 0), money(loss.get("unit_cost")), money(loss.get("total_cost")),
                     loss.get("reason", "-")])
    return rows


def rs17(db, params):
    rows = []
    for alert in db.risk_alerts.find(date_range({}, "created_at", params)).sort("created_at", -1).limit(params.limit):
        rows.append([moment(alert.get("created_at")), alert.get("type", "-"), alert.get("severity", "-"),
                     alert.get("status", "-"), alert.get("entity_type", "-"), alert.get("message", "-"),
                     alert.get("resolution", "-")])
    return rows


def rs18(db, params):
    rows = []
    for payment in db.payments.find(date_range({}, "created_at", params)).sort("created_at", -1).limit(params.limit):
        sale = db.sales.find_one({"_id": payment["sale_id"]}) or {}
        number = sale.get("number", "-")
        if not matches(params, number, payment.get("method"), payment.get("provider")): continue
        rows.append([moment(payment.get("created_at")), number, payment.get("method", "-"), payment.get("status", "-"),
                     money(payment.get("amount")), payment.get("provider", "-"),
                     payment.get("provider_reference", "-"), payment.get("last4") or "-"])
    return rows


def rs19(db, params):
    rows = []
    for user in db.users.find().sort("created_at", -1).limit(params.limit):
        if not matches(params, user.get("name"), user.get("email")): continue
        rows.append([user.get("name", "-"), user.get("email", "-"), ", ".join(user.get("roles", [])) or "-",
                     user.get("status", "-"), user.get("failed_attempts", 0), moment(user.get("created_at"))])
    return rows


def rs20(db, params):
    rows = []
    for event in db.audit_events.find(date_range({}, "occurred_at", params)).sort("occurred_at", -1).limit(params.limit):
        if not matches(params, event.get("action"), event.get("actor_id"), event.get("entity_type")): continue
        rows.append([moment(event.get("occurred_at")), event.get("actor_id", "-"), event.get("action", "-"),
                     event.get("entity_type", "-"), event.get("entity_id") or "-", event.get("outcome", "-")])
    return rows


RUNNERS = {"RS-01": rs01, "RS-02": rs02, "RS-03": rs03, "RS-04": rs04, "RS-05": rs05, "RS-06": rs06, "RS-07": rs07,
           "RS-08": rs08, "RS-09": rs09, "RS-10": rs10, "RS-11": rs11, "RS-12": rs12, "RS-13": rs13, "RS-14": rs14,
           "RS-15": rs15, "RS-16": rs16, "RS-17": rs17, "RS-18": rs18, "RS-19": rs19, "RS-20": rs20}


def run_simple(db, report_id, params):
    report = {**SIMPLE_BY_ID[report_id], "tipo": "simple", "data_layer": "mongodb"}
    rows = check_width(report, RUNNERS[report_id](db, params))
    return {"report": report, "rows": rows, "total": len(rows)}
