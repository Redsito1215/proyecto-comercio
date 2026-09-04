from backend.app import create_app


def test_promotion_requires_products():
    response=create_app(testing=True).test_client().post('/api/v1/promotions',json={})
    assert response.status_code==422


def test_promotions_list_contract():
    response=create_app(testing=True).test_client().get('/api/v1/promotions')
    assert response.status_code==200 and 'data' in response.get_json()
