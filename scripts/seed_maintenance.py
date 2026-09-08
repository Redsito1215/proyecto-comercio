"""Carga idempotente de datos operativos ficticios para demostracion.

No elimina datos creados por usuarios. Al repetirse, solo reemplaza los registros
marcados con SEED_BATCH y conserva cuentas, roles y configuracion de seguridad.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from random import Random

from bson import Decimal128, ObjectId

from backend.db import get_db
from backend.modules.customers.services import recalculate_customer
from backend.modules.forecasting.schemas import ForecastRunCreate
from backend.modules.forecasting.services import create_run


SEED_BATCH = "maintenance-v1"
LOCATION = "main"


def money(value):
    return Decimal128(Decimal(str(value)).quantize(Decimal("0.01")))


def upsert_id(collection, query, values):
    collection.update_one(
        query,
        {"$set": {**values, "seed_batch": SEED_BATCH}, "$setOnInsert": {"created_at": values.get("created_at", datetime.now(UTC))}},
        upsert=True,
    )
    return collection.find_one(query)["_id"]


def seed():
    db = get_db()
    now = datetime.now(UTC)
    rng = Random(20260908)

    # Solo se regeneran hechos de esta carga; nunca se borran datos del usuario.
    generated = [
        "purchase_order_items", "purchase_orders", "inventory_movements", "lots",
        "sale_items", "sales", "payments", "cash_movements", "cash_counts",
        "cash_sessions", "loss_events", "lost_sales", "risk_alerts",
        "competitor_prices", "price_changes", "customer_consents",
        "customer_segments", "churn_signals", "promotions", "promotion_audience",
        "promotion_coupons", "notification_outbox", "forecast_runs", "forecasts",
        "report_runs", "audit_events",
    ]
    for name in generated:
        db[name].delete_many({"seed_batch": SEED_BATCH})

    categories = [
        ("BEB", "Bebidas"), ("LAC", "Lácteos"), ("PAN", "Panadería"),
        ("SNA", "Snacks"), ("DES", "Despensa"), ("LIM", "Limpieza"),
        ("HIG", "Higiene personal"), ("CON", "Congelados"),
    ]
    category_ids = {}
    for code, name in categories:
        category_ids[code] = upsert_id(db.categories, {"code": code}, {
            "code": code, "name": name, "name_normalized": name.casefold(), "active": True,
        })

    suppliers = [
        ("SUP-AND", "Distribuidora Andina", "ventas@distribuidora-andina.test", "0990001001"),
        ("SUP-LAC", "Lácteos del Valle", "pedidos@lacteos-valle.test", "0990001002"),
        ("SUP-PAN", "Panificadora Central", "comercial@panificadora-central.test", "0990001003"),
        ("SUP-HOG", "Suministros Hogar", "pedidos@suministros-hogar.test", "0990001004"),
    ]
    supplier_ids = {}
    for code, name, email, phone in suppliers:
        supplier_ids[code] = upsert_id(db.suppliers, {"code": code}, {
            "code": code, "name": name, "name_normalized": name.casefold(),
            "email": email, "phone": phone, "active": True,
        })

    locations = [
        ("MAIN", "Sucursal principal", "Av. 9 de Octubre 410, Guayaquil"),
        ("NORTE", "Sucursal norte", "Av. Francisco de Orellana 221, Guayaquil"),
        ("BOD-01", "Bodega central", "Vía a Daule km 8.5, Guayaquil"),
    ]
    for code, name, address in locations:
        upsert_id(db.locations, {"code": code}, {
            "code": code, "name": name, "name_normalized": name.casefold(),
            "address": address, "active": True,
        })

    products = [
        ("CAF-001", "Café molido premium 400 g", "8.50", "4.20", False, "7861000000011", "DES", 38),
        ("LEC-001", "Leche entera 1 L", "1.60", "1.05", True, "7861000000028", "LAC", 24),
        ("PAT-001", "Patatas artesanales 150 g", "2.40", "1.10", True, "7861000000035", "SNA", 17),
        ("CER-000", "Cerveza sin alcohol 330 ml", "1.90", "0.85", False, "7861000000042", "BEB", 42),
        ("BOL-001", "Bollos de mantequilla x4", "2.10", "0.95", True, "7861000000059", "PAN", 12),
        ("ARR-001", "Arroz premium 1 kg", "2.25", "1.30", False, "7861000000066", "DES", 55),
        ("YOG-001", "Yogur natural 200 g", "1.15", "0.62", True, "7861000000073", "LAC", 20),
        ("AGU-001", "Agua mineral 1 L", "0.85", "0.32", False, "7861000000080", "BEB", 68),
        ("DET-001", "Detergente líquido 1 L", "4.75", "2.80", False, "7861000000097", "LIM", 26),
        ("JAB-001", "Jabón de tocador x3", "3.20", "1.65", False, "7861000000103", "HIG", 31),
        ("POL-001", "Pollo congelado 1 kg", "5.90", "3.95", True, "7861000000110", "CON", 15),
        ("AZU-001", "Azúcar blanca 1 kg", "1.55", "0.88", False, "7861000000127", "DES", 44),
    ]
    product_ids, product_data = {}, {}
    for sku, name, price, cost, perishable, barcode, category, stock in products:
        pid = upsert_id(db.products, {"sku": sku}, {
            "sku": sku, "name": name, "name_normalized": name.casefold(), "unit": "unidad",
            "barcode": barcode, "current_price": money(price), "average_cost": money(cost),
            "perishable": perishable, "minimum_margin_percent": money("20"),
            "category_id": category_ids[category], "active": True, "updated_at": now,
        })
        product_ids[sku] = pid
        product_data[sku] = {"name": name, "price": Decimal(price), "cost": Decimal(cost), "stock": stock, "perishable": perishable}
        upsert_id(db.inventory, {"product_id": pid, "location_id": LOCATION}, {
            "product_id": pid, "location_id": LOCATION, "on_hand": stock,
            "available": stock, "reserved": 0, "average_cost": money(cost), "updated_at": now,
        })
        if perishable:
            lot_id = ObjectId()
            db.lots.insert_one({
                "_id": lot_id, "product_id": pid, "location_id": LOCATION,
                "lot_number": f"LOT-{sku}-{now:%y%m}", "quantity": stock,
                "available_quantity": stock, "unit_cost": money(cost),
                "expires_at": now + timedelta(days=18 + rng.randrange(35)),
                "status": "available", "created_at": now - timedelta(days=12),
                "updated_at": now, "seed_batch": SEED_BATCH,
            })

    customers = [
        ("CLI-001", "Ana Torres", "ana.torres@clientes.test", "0992103001", datetime(1992, 9, 10, tzinfo=UTC)),
        ("CLI-002", "Carlos Méndez", "carlos.mendez@clientes.test", "0992103002", datetime(1987, 2, 18, tzinfo=UTC)),
        ("CLI-003", "Sofía Ruiz", "sofia.ruiz@clientes.test", "0992103003", datetime(1998, 12, 3, tzinfo=UTC)),
        ("CLI-004", "Daniel Vera", "daniel.vera@clientes.test", "0992103004", datetime(1985, 6, 24, tzinfo=UTC)),
        ("CLI-005", "María Zambrano", "maria.zambrano@clientes.test", "0992103005", datetime(1990, 4, 9, tzinfo=UTC)),
        ("CLI-006", "José Cedeño", "jose.cedeno@clientes.test", "0992103006", datetime(1979, 11, 16, tzinfo=UTC)),
        ("CLI-007", "Valentina López", "valentina.lopez@clientes.test", "0992103007", datetime(2001, 8, 28, tzinfo=UTC)),
        ("CLI-008", "Andrés Paredes", "andres.paredes@clientes.test", "0992103008", datetime(1995, 1, 30, tzinfo=UTC)),
    ]
    customer_ids = []
    for code, name, email, phone, birthday in customers:
        cid = upsert_id(db.customers, {"code": code}, {
            "code": code, "name": name, "name_normalized": name.casefold(), "email": email,
            "email_normalized": email, "phone": phone, "birthday": birthday,
            "status": "active", "updated_at": now,
        })
        customer_ids.append(cid)
        for channel in ("email", "sms"):
            db.customer_consents.insert_one({
                "customer_id": cid, "purpose": "marketing", "channel": channel,
                "status": "granted" if not (code == "CLI-006" and channel == "sms") else "revoked",
                "source": "formulario_en_tienda", "granted_at": now - timedelta(days=120),
                "updated_at": now - timedelta(days=20), "seed_batch": SEED_BATCH,
            })

    # Tres compras históricas ya recibidas.
    for idx, (supplier_code, age, lines) in enumerate([
        ("SUP-AND", 75, [("CAF-001", 30), ("ARR-001", 60), ("AGU-001", 80)]),
        ("SUP-LAC", 42, [("LEC-001", 48), ("YOG-001", 36), ("POL-001", 24)]),
        ("SUP-HOG", 18, [("DET-001", 24), ("JAB-001", 36), ("AZU-001", 40)]),
    ], 1):
        created = now - timedelta(days=age)
        total = sum(product_data[sku]["cost"] * qty for sku, qty in lines)
        oid = ObjectId()
        db.purchase_orders.insert_one({
            "_id": oid, "number": f"OC-MNT-{idx:04d}", "supplier_id": supplier_ids[supplier_code],
            "supplier_name": db.suppliers.find_one({"_id": supplier_ids[supplier_code]})["name"],
            "location_id": LOCATION, "status": "received", "total": money(total),
            "created_at": created, "updated_at": created + timedelta(days=2), "seed_batch": SEED_BATCH,
        })
        for sku, qty in lines:
            db.purchase_order_items.insert_one({
                "purchase_order_id": oid, "product_id": product_ids[sku], "sku": sku,
                "name": product_data[sku]["name"], "quantity": qty, "received_quantity": qty,
                "pending_quantity": 0, "unit_cost": money(product_data[sku]["cost"]),
                "line_total": money(product_data[sku]["cost"] * qty), "seed_batch": SEED_BATCH,
            })
            db.inventory_movements.insert_one({
                "product_id": product_ids[sku], "location_id": LOCATION, "type": "receipt",
                "quantity": qty, "unit_cost": money(product_data[sku]["cost"]),
                "source_type": "purchase_order", "source_id": oid,
                "occurred_at": created + timedelta(days=2), "seed_batch": SEED_BATCH,
            })

    # Ventas de los últimos 90 días, con varios medios de pago y clientes recurrentes.
    methods = ["cash", "cash", "card", "card", "transfer"]
    skus = list(product_ids)
    sales_total = Decimal("0")
    for index in range(72):
        # Distribuye el historial completo hasta hoy (incluye actividad reciente).
        age = round((71 - index) * 89 / 71)
        sold_at = now - timedelta(days=age, hours=rng.randrange(1, 10), minutes=rng.randrange(60))
        chosen = rng.sample(skus, rng.randint(1, 4))
        cid = customer_ids[index % len(customer_ids)] if index % 5 else None
        sale_id = ObjectId()
        subtotal = Decimal("0")
        items = []
        for sku in chosen:
            qty = rng.randint(1, 3)
            info = product_data[sku]
            line_total = info["price"] * qty
            subtotal += line_total
            items.append({
                "sale_id": sale_id, "product_id": product_ids[sku], "sku": sku, "name": info["name"],
                "quantity": qty, "unit_price": money(info["price"]), "unit_cost": money(info["cost"]),
                "line_total": money(line_total), "seed_batch": SEED_BATCH,
            })
        discount = (subtotal * Decimal("0.10")).quantize(Decimal("0.01")) if index in (58, 65, 70) else Decimal("0")
        total = subtotal - discount
        sales_total += total
        db.sales.insert_one({
            "_id": sale_id, "number": f"VTA-MNT-{index + 1:05d}", "location_id": LOCATION,
            "customer_id": cid, "status": "confirmed", "payment_status": "paid",
            "subtotal": money(subtotal), "discount_total": money(discount), "total": money(total),
            "paid_amount": money(total), "idempotency_key": f"maintenance-sale-{index + 1}",
            "created_at": sold_at, "confirmed_at": sold_at, "paid_at": sold_at,
            "updated_at": sold_at, "version": 3, "seed_batch": SEED_BATCH,
        })
        db.sale_items.insert_many(items)
        method = methods[index % len(methods)]
        payment_id = ObjectId()
        db.payments.insert_one({
            "_id": payment_id, "sale_id": sale_id, "method": method, "amount": money(total),
            "status": "approved", "provider": "internal-cash" if method == "cash" else "sandbox-tokenized",
            "provider_reference": f"PAY-MNT-{index + 1:06d}", "idempotency_key": f"maintenance-payment-{index + 1}",
            "last4": None if method != "card" else f"{4100 + index:04d}"[-4:],
            "created_at": sold_at + timedelta(minutes=2), "processed_at": sold_at + timedelta(minutes=2),
            "seed_batch": SEED_BATCH,
        })
        for item in items:
            db.inventory_movements.insert_one({
                "product_id": item["product_id"], "location_id": LOCATION, "type": "sale",
                "quantity": -item["quantity"], "unit_cost": item["unit_cost"], "source_type": "sale",
                "source_id": sale_id, "occurred_at": sold_at, "seed_batch": SEED_BATCH,
            })

    # Historial de cierres de caja y una caja abierta para continuar la prueba manual.
    for week in range(4, 0, -1):
        opened = now - timedelta(days=week * 7, hours=8)
        sid = ObjectId()
        expected = Decimal("230") + Decimal(str(week * 17))
        difference = Decimal("-2.00") if week == 2 else Decimal("0")
        db.cash_sessions.insert_one({
            "_id": sid, "register_id": "CAJA-01", "location_id": LOCATION, "status": "closed",
            "opening_amount": money("100"), "expected_balance": money(expected),
            "counted_balance": money(expected + difference), "difference": money(difference),
            "opened_at": opened, "closed_at": opened + timedelta(hours=10),
            "close_reason": "Cierre diario", "created_at": opened, "seed_batch": SEED_BATCH,
        })
        db.cash_movements.insert_one({
            "session_id": sid, "type": "sale", "direction": "in", "amount": money(expected - Decimal("100")),
            "source_type": "daily_summary", "reason": "Cobros en efectivo del turno",
            "occurred_at": opened + timedelta(hours=9), "seed_batch": SEED_BATCH,
        })
        count_id = db.cash_counts.insert_one({
            "session_id": sid, "expected": money(expected), "counted": money(expected + difference),
            "difference": money(difference), "reason": "Arqueo de cierre", "counted_at": opened + timedelta(hours=10),
            "is_closing": True, "seed_batch": SEED_BATCH,
        }).inserted_id
        if difference:
            db.risk_alerts.insert_one({
                "type": "cash_difference", "severity": "medium", "entity_type": "cash_session",
                "entity_id": sid, "evidence": {"cash_count_id": count_id, "difference": money(difference)},
                "status": "resolved", "message": "Diferencia de caja revisada y justificada",
                "resolution": "Comprobante de gasto menor validado", "created_at": opened + timedelta(hours=10),
                "resolved_at": opened + timedelta(days=1), "seed_batch": SEED_BATCH,
            })
    open_sid = ObjectId()
    db.cash_sessions.insert_one({
        "_id": open_sid, "register_id": "CAJA-01", "location_id": LOCATION, "status": "open",
        "opening_amount": money("100"), "opened_at": now - timedelta(hours=2),
        "created_at": now - timedelta(hours=2), "seed_batch": SEED_BATCH,
    })
    db.cash_movements.insert_one({
        "session_id": open_sid, "type": "deposit", "direction": "in", "amount": money("25"),
        "source_type": "cash_float", "reason": "Refuerzo de cambio para el turno",
        "idempotency_key": "maintenance-open-cash", "occurred_at": now - timedelta(hours=1),
        "seed_batch": SEED_BATCH,
    })

    # Mermas, ventas perdidas y precios observados explican los tableros analíticos.
    for idx, (sku, loss_type, qty, age, reason) in enumerate([
        ("LEC-001", "expired", 3, 20, "Fecha de caducidad alcanzada"),
        ("BOL-001", "damaged", 2, 11, "Empaque dañado durante reposición"),
        ("YOG-001", "expired", 4, 5, "Rotación FEFO incompleta"),
        ("PAT-001", "shrinkage", 1, 2, "Diferencia detectada en conteo"),
    ]):
        info = product_data[sku]
        db.loss_events.insert_one({
            "product_id": product_ids[sku], "location_id": LOCATION, "type": loss_type,
            "quantity": qty, "unit_cost": money(info["cost"]), "total_cost": money(info["cost"] * qty),
            "reason": reason, "occurred_at": now - timedelta(days=age), "seed_batch": SEED_BATCH,
        })
    for sku, qty, age in [("CAF-001", 4, 14), ("LEC-001", 3, 8), ("POL-001", 2, 3)]:
        db.lost_sales.insert_one({
            "product_id": product_ids[sku], "location_id": LOCATION,
            "requested_quantity": qty, "reason": "out_of_stock",
            "occurred_at": now - timedelta(days=age), "seed_batch": SEED_BATCH,
        })
    competitors = ["Supermercado Centro", "Tienda del Barrio", "Mercado Digital"]
    for sku in skus:
        own = product_data[sku]["price"]
        for offset, competitor in enumerate(competitors):
            observed = (own * (Decimal("0.96") + Decimal(str(offset)) * Decimal("0.035"))).quantize(Decimal("0.01"))
            db.competitor_prices.insert_one({
                "product_id": product_ids[sku], "competitor": competitor,
                "observed_price": money(observed), "observed_at": now - timedelta(days=offset * 3 + 1),
                "source": "levantamiento_manual", "created_at": now - timedelta(days=offset * 3 + 1),
                "seed_batch": SEED_BATCH,
            })
    for sku, old, new, age, reason in [
        ("CAF-001", "8.20", "8.50", 35, "Actualización de costo del proveedor"),
        ("LEC-001", "1.55", "1.60", 21, "Ajuste competitivo semanal"),
        ("DET-001", "4.90", "4.75", 9, "Precio de atracción por rotación"),
    ]:
        cost = product_data[sku]["cost"]
        margin = ((Decimal(new) - cost) / Decimal(new) * 100).quantize(Decimal("0.01"))
        db.price_changes.insert_one({
            "product_id": product_ids[sku], "old_price": money(old), "new_price": money(new),
            "cost_snapshot": money(cost), "margin_percent": money(margin), "reason": reason,
            "effective_at": now - timedelta(days=age), "created_at": now - timedelta(days=age),
            "seed_batch": SEED_BATCH,
        })

    for cid in customer_ids:
        recalculate_customer(db, str(cid))
        db.customer_segments.update_one({"customer_id": cid}, {"$set": {"seed_batch": SEED_BATCH}})
        db.churn_signals.update_one({"customer_id": cid}, {"$set": {"seed_batch": SEED_BATCH}})

    promo_id = ObjectId()
    db.promotions.insert_one({
        "_id": promo_id, "name": "Semana del desayuno", "discount_percent": money("10"),
        "product_ids": [product_ids["CAF-001"], product_ids["LEC-001"], product_ids["BOL-001"]],
        "segment": "frequent", "channel": "email", "valid_from": now - timedelta(days=5),
        "valid_until": now + timedelta(days=9), "control_percent": 20, "usage_limit": 1,
        "status": "active", "created_at": now - timedelta(days=7), "updated_at": now,
        "seed_batch": SEED_BATCH,
    })
    for idx, cid in enumerate(customer_ids):
        group = "control" if idx % 5 == 0 else "treatment"
        db.promotion_audience.insert_one({
            "promotion_id": promo_id, "customer_id": cid,
            "customer_name": db.customers.find_one({"_id": cid})["name"], "eligible": True,
            "reason": "Cliente frecuente con consentimiento vigente", "group": group,
            "consent_snapshot": True, "assigned_at": now - timedelta(days=6), "seed_batch": SEED_BATCH,
        })
        if group == "treatment":
            coupon_id = ObjectId()
            code = f"DESAYUNO-{idx + 1:03d}"
            db.promotion_coupons.insert_one({
                "_id": coupon_id, "promotion_id": promo_id, "customer_id": cid, "code": code,
                "status": "active", "usage_limit": 1, "usage_count": 0,
                "valid_from": now - timedelta(days=5), "valid_until": now + timedelta(days=9),
                "created_at": now - timedelta(days=5), "seed_batch": SEED_BATCH,
            })
            db.notification_outbox.insert_one({
                "promotion_id": promo_id, "customer_id": cid, "channel": "email", "status": "sent",
                "payload": {"coupon_code": code, "promotion": "Semana del desayuno"},
                "created_at": now - timedelta(days=5), "sent_at": now - timedelta(days=5, minutes=-2),
                "seed_batch": SEED_BATCH,
            })

    run = create_run(db, ForecastRunCreate(location_id=LOCATION, horizon_days=14, lookback_days=90), "maintenance-seed")
    db.forecast_runs.update_one({"_id": ObjectId(run["id"])}, {"$set": {"seed_batch": SEED_BATCH}})
    db.forecasts.update_many({"run_id": ObjectId(run["id"])}, {"$set": {"seed_batch": SEED_BATCH}})

    for action, entity, age in [
        ("inventory.receipt", "purchase_order", 18), ("price.apply", "product", 9),
        ("promotion.activate", "promotion", 5), ("forecast.run", "forecast", 0),
        ("cash.open", "cash_session", 0),
    ]:
        db.audit_events.insert_one({
            "actor_id": "maintenance-seed", "action": action, "entity_type": entity,
            "entity_id": None, "outcome": "success", "metadata": {"origin": "operational_demo"},
            "occurred_at": now - timedelta(days=age), "seed_batch": SEED_BATCH,
        })

    db.settings.update_one({"key": "business"}, {"$set": {
        "business_name": "Comercio Inteligente", "tax_id": "0999999999001", "currency": "USD",
        "timezone": "America/Guayaquil", "low_stock_threshold": 8,
        "expiry_warning_days": 30, "updated_at": now,
    }}, upsert=True)

    counts = {name: db[name].count_documents({}) for name in [
        "products", "inventory", "customers", "sales", "payments", "purchase_orders",
        "cash_sessions", "loss_events", "competitor_prices", "promotions", "forecasts", "audit_events",
    ]}
    print("Carga operativa completada sin borrar datos del usuario.")
    print(" | ".join(f"{name}: {count}" for name, count in counts.items()))
    print(f"Ventas históricas sembradas: 72 | Importe: ${sales_total.quantize(Decimal('0.01'))}")


if __name__ == "__main__":
    seed()
