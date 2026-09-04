from backend.app import create_app


def test_cash_open_validates_amount():
    response=create_app(testing=True).test_client().post('/api/v1/controls/cash-sessions',json={'register_id':'C1','opening_amount':-1})
    assert response.status_code==422


def test_movement_requires_idempotency_key():
    response=create_app(testing=True).test_client().post('/api/v1/controls/cash-sessions/000000000000000000000000/movements',json={'type':'deposit','amount':1,'reason':'Cambio'})
    assert response.status_code==400


def test_dashboard_contract():
    response=create_app(testing=True).test_client().get('/api/v1/controls/dashboard')
    assert response.status_code==200 and 'data' in response.get_json()
