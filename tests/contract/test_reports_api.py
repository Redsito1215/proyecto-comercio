from backend.app import create_app


def test_report_rejects_unknown_section():
    response=create_app(testing=True).test_client().post('/api/v1/reports/preview',json={'title':'Prueba','sections':['unknown']})
    assert response.status_code==422


def test_report_pdf_contract():
    response=create_app(testing=True).test_client().post('/api/v1/reports/pdf',json={'title':'Informe vacío','sections':['sales']})
    assert response.status_code==200 and response.mimetype=='application/pdf' and response.data.startswith(b'%PDF-')


def test_analytics_status_contract():
    response=create_app(testing=True).test_client().get('/api/v1/reports/analytics/status')
    assert response.status_code==200
    assert response.get_json()['data']['engine']=='ClickHouse'
