"""Genera ~100k documentos históricos relacionados para pruebas de volumen.

Uso: python -m scripts.seed_bulk
La carga es idempotente y solo reemplaza documentos con seed_batch=volume-100k-v1.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from random import Random

from bson import Decimal128, ObjectId

from backend.db import get_db
from scripts.seed_maintenance import seed as seed_base


BATCH = "volume-100k-v1"
SALES = 15_000
CHUNK = 1_000


def money(value):
    return Decimal128(Decimal(str(value)).quantize(Decimal("0.01")))


def flush(collection, rows):
    if rows:
        collection.insert_many(rows, ordered=False)
        rows.clear()


def seed():
    seed_base()
    db = get_db()
    rng = Random(100_000)
    now = datetime.now(UTC)

    collections = ("sales", "sale_items", "payments", "inventory_movements")
    for name in collections:
        db[name].delete_many({"seed_batch": BATCH})

    products = list(db.products.find({"active": True, "current_price": {"$exists": True}}))
    customers = list(db.customers.find({"status": "active"}, {"_id": 1}))
    if not products:
        raise RuntimeError("No hay productos activos para generar el historial")

    sales, items, payments, movements = [], [], [], []
    revenue = Decimal("0")
    line_count = 0
    for index in range(SALES):
        sale_id = ObjectId()
        # Distribución uniforme en 365 días, dejando ventas en el día actual.
        age_minutes = rng.randrange(0, 365 * 24 * 60)
        sold_at = now - timedelta(minutes=age_minutes)
        chosen = rng.sample(products, rng.randint(1, min(4, len(products))))
        customer_id = None if index % 6 == 0 else customers[index % len(customers)]["_id"]
        subtotal = Decimal("0")

        for product in chosen:
            quantity = rng.randint(1, 3)
            price = product["current_price"].to_decimal()
            cost = product.get("average_cost", Decimal128("0")).to_decimal()
            line_total = (price * quantity).quantize(Decimal("0.01"))
            subtotal += line_total
            common = {
                "sale_id": sale_id, "product_id": product["_id"], "sku": product["sku"],
                "name": product["name"], "quantity": quantity, "unit_price": money(price),
                "unit_cost": money(cost), "line_total": money(line_total), "seed_batch": BATCH,
            }
            items.append(common)
            movements.append({
                "product_id": product["_id"], "location_id": "main", "type": "sale",
                "quantity": -quantity, "unit_cost": money(cost), "source_type": "sale",
                "source_id": sale_id, "occurred_at": sold_at, "seed_batch": BATCH,
            })
            line_count += 1

        discount_rate = Decimal("0.10") if index % 23 == 0 else Decimal("0")
        discount = (subtotal * discount_rate).quantize(Decimal("0.01"))
        total = subtotal - discount
        revenue += total
        sales.append({
            "_id": sale_id, "number": f"VTA-HIS-{index + 1:07d}", "location_id": "main",
            "customer_id": customer_id, "status": "confirmed", "payment_status": "paid",
            "subtotal": money(subtotal), "discount_total": money(discount), "total": money(total),
            "paid_amount": money(total), "idempotency_key": f"volume-sale-{index + 1}",
            "created_at": sold_at, "confirmed_at": sold_at, "paid_at": sold_at,
            "updated_at": sold_at, "version": 3, "seed_batch": BATCH,
        })
        method = ("cash", "card", "transfer", "wallet")[index % 4]
        payments.append({
            "sale_id": sale_id, "method": method, "amount": money(total), "status": "approved",
            "provider": "internal-cash" if method == "cash" else "sandbox-tokenized",
            "provider_reference": f"PAY-HIS-{index + 1:07d}",
            "idempotency_key": f"volume-payment-{index + 1}",
            "last4": f"{index % 10_000:04d}" if method == "card" else None,
            "created_at": sold_at + timedelta(minutes=2),
            "processed_at": sold_at + timedelta(minutes=2), "seed_batch": BATCH,
        })

        if len(sales) >= CHUNK:
            flush(db.sales, sales)
            flush(db.sale_items, items)
            flush(db.payments, payments)
            flush(db.inventory_movements, movements)

    flush(db.sales, sales)
    flush(db.sale_items, items)
    flush(db.payments, payments)
    flush(db.inventory_movements, movements)

    generated = {name: db[name].count_documents({"seed_batch": BATCH}) for name in collections}
    total = sum(generated.values())
    print("Carga masiva completada.")
    print(" | ".join(f"{name}: {count}" for name, count in generated.items()))
    print(f"Documentos relacionados: {total:,} | Ventas: {SALES:,} | Líneas: {line_count:,}")
    print(f"Facturación histórica simulada: ${revenue:,.2f}")


if __name__ == "__main__":
    seed()
