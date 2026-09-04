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


def load_operational_facts():
    mongo=MongoClient(os.environ["MONGO_URI"])[os.getenv("MONGO_DB","comercio_inteligente")]
    click=clickhouse_connect.get_client(host=os.getenv("CLICKHOUSE_HOST","clickhouse"),database=os.getenv("CLICKHOUSE_DATABASE","comercio_analytics"));loaded=datetime.utcnow();sales=list(mongo.sales.find({"status":{"$in":["confirmed","partially_returned"]}}))
    sale_rows=[(str(x["_id"]),x.get("number",""),x.get("confirmed_at") or x.get("created_at"),x.get("location_id","main"),str(x["customer_id"]) if x.get("customer_id") else None,x["status"],decimal_value(x.get("total")),loaded) for x in sales]
    if sale_rows:click.insert("sales_facts",sale_rows,column_names=["sale_id","sale_number","occurred_at","location_id","customer_id","status","total","loaded_at"])
    sale_ids=[x["_id"] for x in sales];item_rows=[]
    for x in mongo.sale_items.find({"sale_id":{"$in":sale_ids}}):item_rows.append((str(x["sale_id"]),str(x["product_id"]),x.get("sku",""),x.get("name",""),x["quantity"],decimal_value(x.get("unit_price")),decimal_value(x.get("unit_cost")),decimal_value(x.get("line_total")),loaded))
    if item_rows:click.insert("sale_item_facts",item_rows,column_names=["sale_id","product_id","sku","product_name","quantity","unit_price","unit_cost","line_total","loaded_at"])
    stocks=[(loaded,str(x["product_id"]),x.get("location_id","main"),x.get("on_hand",0),x.get("available",0),decimal_value(x.get("average_cost"))) for x in mongo.inventory.find()]
    if stocks:click.insert("inventory_snapshots",stocks,column_names=["captured_at","product_id","location_id","on_hand","available","average_cost"])


with DAG("comercio_inteligente_etl",start_date=datetime(2026,1,1),schedule="0 * * * *",catchup=False,default_args={"retries":2,"retry_delay":timedelta(minutes=2)},tags=["comercio","clickhouse"]) as dag:
    PythonOperator(task_id="mongo_to_clickhouse",python_callable=load_operational_facts)
