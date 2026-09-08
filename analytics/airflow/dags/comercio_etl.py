import os
from datetime import datetime,timedelta
from decimal import Decimal

import clickhouse_connect
from airflow import DAG
from airflow.operators.python import PythonOperator
from bson import Decimal128
from pymongo import MongoClient


def decimal_value(value):
    return value.to_decimal() if isinstance(value,Decimal128) else Decimal(str(value or 0))


def text(value,default=""):
    return str(value) if value is not None else default


def insert(click,table,rows,columns):
    """Inserta y consolida: ReplacingMergeTree deduplica en segundo plano y una
    ejecución repetida mostraría filas duplicadas hasta que el merge ocurriera."""
    if not rows:return
    click.insert(table,rows,column_names=columns)
    click.command(f"OPTIMIZE TABLE {table} FINAL")


def load_operational_facts():
    mongo=MongoClient(os.environ["MONGO_URI"])[os.getenv("MONGO_DB","comercio_inteligente")]
    click=clickhouse_connect.get_client(host=os.getenv("CLICKHOUSE_HOST","clickhouse"),database=os.getenv("CLICKHOUSE_DATABASE","comercio_analytics"));loaded=datetime.utcnow();sales=list(mongo.sales.find({"status":{"$in":["confirmed","partially_returned"]}}))
    sale_rows=[(str(x["_id"]),x.get("number",""),x.get("confirmed_at") or x.get("created_at"),x.get("location_id","main"),str(x["customer_id"]) if x.get("customer_id") else None,x["status"],decimal_value(x.get("total")),loaded) for x in sales]
    insert(click,"sales_facts",sale_rows,["sale_id","sale_number","occurred_at","location_id","customer_id","status","total","loaded_at"])
    sale_ids=[x["_id"] for x in sales];item_rows=[]
    for x in mongo.sale_items.find({"sale_id":{"$in":sale_ids}}):item_rows.append((str(x["sale_id"]),str(x["product_id"]),x.get("sku",""),x.get("name",""),x["quantity"],decimal_value(x.get("unit_price")),decimal_value(x.get("unit_cost")),decimal_value(x.get("line_total")),loaded))
    insert(click,"sale_item_facts",item_rows,["sale_id","product_id","sku","product_name","quantity","unit_price","unit_cost","line_total","loaded_at"])
    stocks=[(loaded,str(x["product_id"]),x.get("location_id","main"),x.get("on_hand",0),x.get("available",0),decimal_value(x.get("average_cost"))) for x in mongo.inventory.find()]
    if stocks:click.insert("inventory_snapshots",stocks,column_names=["captured_at","product_id","location_id","on_hand","available","average_cost"])


def load_product_dimension():
    """Categoría y proveedor no viajan en las líneas de venta, así que se cargan
    aparte para que los informes compuestos puedan agrupar por ellos."""
    mongo=MongoClient(os.environ["MONGO_URI"])[os.getenv("MONGO_DB","comercio_inteligente")]
    click=clickhouse_connect.get_client(host=os.getenv("CLICKHOUSE_HOST","clickhouse"),database=os.getenv("CLICKHOUSE_DATABASE","comercio_analytics"));loaded=datetime.utcnow()
    categories={x["_id"]:x.get("name","") for x in mongo.categories.find()};suppliers={x["_id"]:x.get("name","") for x in mongo.suppliers.find()}
    rows=[(str(x["_id"]),x.get("sku",""),x.get("name",""),categories.get(x.get("category_id"),"sin categoría"),suppliers.get(x.get("supplier_id"),"sin proveedor"),decimal_value(x.get("current_price")),decimal_value(x.get("average_cost")),decimal_value(x.get("minimum_margin_percent")),1 if x.get("active") else 0,loaded) for x in mongo.products.find()]
    insert(click,"product_dim",rows,["product_id","sku","name","category","supplier","current_price","average_cost","minimum_margin_percent","active","loaded_at"])


def load_control_facts():
    mongo=MongoClient(os.environ["MONGO_URI"])[os.getenv("MONGO_DB","comercio_inteligente")]
    click=clickhouse_connect.get_client(host=os.getenv("CLICKHOUSE_HOST","clickhouse"),database=os.getenv("CLICKHOUSE_DATABASE","comercio_analytics"));loaded=datetime.utcnow()
    payments=[(str(x["_id"]),str(x["sale_id"]),x.get("method",""),x.get("status",""),text(x.get("provider")),decimal_value(x.get("amount")),x.get("created_at"),loaded) for x in mongo.payments.find()]
    insert(click,"payment_facts",payments,["payment_id","sale_id","method","status","provider","amount","occurred_at","loaded_at"])
    losses=[(str(x["_id"]),str(x["product_id"]),x.get("location_id","main"),x.get("type",""),x.get("quantity",0),decimal_value(x.get("unit_cost")),decimal_value(x.get("total_cost")),text(x.get("reason")),x.get("occurred_at"),loaded) for x in mongo.loss_events.find()]
    insert(click,"loss_facts",losses,["loss_id","product_id","location_id","loss_type","quantity","unit_cost","total_cost","reason","occurred_at","loaded_at"])
    sessions=[(str(x["_id"]),x.get("register_id",""),x.get("location_id","main"),x.get("status",""),decimal_value(x.get("opening_amount")),decimal_value(x.get("expected_balance")),decimal_value(x.get("counted_balance")),decimal_value(x.get("difference")),text(x.get("opened_by")),text(x.get("closed_by")),x.get("opened_at"),loaded) for x in mongo.cash_sessions.find()]
    insert(click,"cash_session_facts",sessions,["session_id","register_id","location_id","status","opening_amount","expected_balance","counted_balance","difference","opened_by","closed_by","opened_at","loaded_at"])


def load_commercial_facts():
    mongo=MongoClient(os.environ["MONGO_URI"])[os.getenv("MONGO_DB","comercio_inteligente")]
    click=clickhouse_connect.get_client(host=os.getenv("CLICKHOUSE_HOST","clickhouse"),database=os.getenv("CLICKHOUSE_DATABASE","comercio_analytics"));loaded=datetime.utcnow()
    segments={x["customer_id"]:x for x in mongo.customer_segments.find()};churn={x["customer_id"]:x for x in mongo.churn_signals.find()};customers=[]
    for customer in mongo.customers.find():
        segment=segments.get(customer["_id"],{});signal=churn.get(customer["_id"],{})
        customers.append((str(customer["_id"]),customer.get("name",""),segment.get("segment","sin_historial"),segment.get("frequency",0),decimal_value(segment.get("spend")),decimal_value(segment.get("margin")),decimal_value(segment.get("score")),signal.get("status","sin_datos"),int(signal.get("delay_days") or 0),loaded))
    insert(click,"customer_facts",customers,["customer_id","name","segment","frequency","spend","margin","score","churn_status","delay_days","loaded_at"])
    promotions={x["_id"]:x for x in mongo.promotions.find()};audience=[]
    for row in mongo.promotion_audience.find():
        promotion=promotions.get(row["promotion_id"])
        if not promotion:continue
        audience.append((str(row["promotion_id"]),promotion.get("name",""),str(row["customer_id"]),row.get("group","excluded"),1 if row.get("eligible") else 0,decimal_value(promotion.get("discount_percent")),promotion["valid_from"],promotion["valid_until"],loaded))
    insert(click,"promotion_audience_facts",audience,["promotion_id","promotion_name","customer_id","experimental_group","eligible","discount_percent","valid_from","valid_until","loaded_at"])
    runs={x["_id"]:x for x in mongo.forecast_runs.find({"status":"completed"})};forecasts=[]
    for row in mongo.forecasts.find({"run_id":{"$in":list(runs)}}):
        run=runs[row["run_id"]]
        forecasts.append((str(row["run_id"]),run.get("cutoff_at") or run.get("created_at"),str(row["product_id"]),row.get("sku",""),row.get("product_name",""),row.get("location_id","main"),row.get("expected_units",0),row.get("lower_bound",0),row.get("upper_bound",0),text(row.get("confidence"),"low"),row.get("available",0),row.get("recommended_quantity",0),loaded))
    insert(click,"forecast_facts",forecasts,["run_id","cutoff_at","product_id","sku","product_name","location_id","expected_units","lower_bound","upper_bound","confidence","available","recommended_quantity","loaded_at"])


with DAG("comercio_inteligente_etl",start_date=datetime(2026,1,1),schedule="0 * * * *",catchup=False,default_args={"retries":2,"retry_delay":timedelta(minutes=2)},tags=["comercio","clickhouse"]) as dag:
    operational=PythonOperator(task_id="mongo_to_clickhouse",python_callable=load_operational_facts)
    dimension=PythonOperator(task_id="product_dimension",python_callable=load_product_dimension)
    controls=PythonOperator(task_id="control_facts",python_callable=load_control_facts)
    commercial=PythonOperator(task_id="commercial_facts",python_callable=load_commercial_facts)
    # La dimensión se carga antes que los hechos que la referencian para que un
    # informe consultado a mitad de la corrida no muestre "sin categoría".
    dimension>>[operational,controls,commercial]
