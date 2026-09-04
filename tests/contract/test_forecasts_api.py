from backend.app import create_app


def test_forecast_run_validates_horizon():
    response=create_app(testing=True).test_client().post('/api/v1/forecasts/runs',json={'horizon_days':0})
    assert response.status_code==422


def test_latest_forecast_contract():
    response=create_app(testing=True).test_client().get('/api/v1/forecasts/latest')
    assert response.status_code==200 and 'data' in response.get_json()
