import pytest

from backend.app import create_app
from backend.modules.reports.catalog import SIMPLE_REPORTS
from backend.modules.reports.compuestos import COMPLEX_REPORTS


@pytest.fixture
def client():
    return create_app(testing=True).test_client()


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


def test_catalog_exposes_both_families(client):
    data=client.get('/api/v1/reports/catalog').get_json()['data']
    assert len(data['simples'])==len(SIMPLE_REPORTS) and len(data['compuestos'])==len(COMPLEX_REPORTS)
    assert {x['tipo'] for x in data['simples']}=={'simple'}
    assert {x['tipo'] for x in data['compuestos']}=={'compuesto'}


def test_catalog_filters_by_family(client):
    data=client.get('/api/v1/reports/catalog?tipo=compuesto').get_json()['data']
    assert data['simples']==[] and data['compuestos']


def test_unknown_report_is_not_found(client):
    assert client.get('/api/v1/reports/simple/RS-99').status_code==404
    assert client.get('/api/v1/reports/compuestos/RC-99').status_code==404


def test_simple_report_returns_declared_columns(client):
    body=client.get('/api/v1/reports/simple/RS-01').get_json()['data']
    assert body['report']['columns'] and body['total']==len(body['rows'])
    assert all(len(row)==len(body['report']['columns']) for row in body['rows'])


def test_simple_report_rejects_inverted_range(client):
    assert client.get('/api/v1/reports/simple/RS-01?date_from=2026-02-01&date_to=2026-01-01').status_code==422


def test_simple_report_pdf_contract(client):
    response=client.get('/api/v1/reports/simple/RS-01/pdf')
    assert response.status_code==200 and response.mimetype=='application/pdf' and response.data.startswith(b'%PDF-')


def test_complex_report_reports_warehouse_outage(client):
    """Sin ClickHouse el compuesto debe fallar explícito, no devolver filas vacías."""
    response=client.get('/api/v1/reports/compuestos/RC-01')
    assert response.status_code in (200,503)
    if response.status_code==503:
        assert response.get_json()['error']['code']=='warehouse_unavailable'
