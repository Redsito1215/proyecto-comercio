from datetime import UTC, datetime, timedelta
from bson import Decimal128
from backend.app import create_app
from backend.db import get_db


def test_forecast_includes_lost_sales_and_is_versioned():
    db=get_db();assert db.name.endswith('_test')
    for name in ('products','sales','sale_items','lost_sales','forecast_runs','forecasts','inventory'):db[name].delete_many({})
    pid=db.products.insert_one({'sku':'FC-1','name':'Café molido','name_normalized':'cafe molido','active':True,'current_price':Decimal128('5'),'average_cost':Decimal128('3')}).inserted_id
    now=datetime.now(UTC)
    for offset in range(21):
        sid=db.sales.insert_one({'location_id':'main','status':'confirmed','confirmed_at':now-timedelta(days=offset)}).inserted_id
        db.sale_items.insert_one({'sale_id':sid,'product_id':pid,'quantity':2})
    db.lost_sales.insert_one({'product_id':pid,'requested_quantity':7,'reason':'out_of_stock','occurred_at':now-timedelta(days=1)})
    response=create_app(testing=True).test_client().post('/api/v1/forecasts/runs',json={'horizon_days':7,'lookback_days':21,'location_id':'main'})
    assert response.status_code==201
    forecast=db.forecasts.find_one({'product_id':pid})
    assert forecast['expected_units'] > 14
    run=db.forecast_runs.find_one({'_id':forecast['run_id']});assert run['method_version']=='robust-median-v1'
