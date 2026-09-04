from datetime import UTC,datetime
from bson import Decimal128
from backend.app import create_app
from backend.db import get_db


def test_composed_report_snapshot_is_audited():
    db=get_db();assert db.name.endswith('_test');db.report_runs.delete_many({});db.audit_events.delete_many({});db.sales.delete_many({})
    db.sales.insert_one({'number':'VTA-REPORT','status':'confirmed','total':Decimal128('12.50'),'confirmed_at':datetime.now(UTC),'location_id':'main'})
    response=create_app(testing=True).test_client().post('/api/v1/reports/pdf',json={'title':'Informe integral','sections':['sales','inventory','losses']})
    assert response.status_code==200 and len(response.data)>1000
    run=db.report_runs.find_one();assert run['snapshot']['sections'][0]['metrics']['operaciones']==1
    assert db.audit_events.find_one({'action':'report.generate','entity_id':str(run['_id'])}) is not None
