from backend.app import create_app


def test_payment_rejects_raw_card_fields():
    response=create_app(testing=True).test_client().post('/api/v1/payments',headers={'Idempotency-Key':'raw-card'},json={'sale_id':'000000000000000000000000','method':'card','amount':'5','payment_method_token':'tok_approved_test','pan':'4111111111111111','cvv':'123'})
    assert response.status_code==422


def test_payment_requires_idempotency():
    response=create_app(testing=True).test_client().post('/api/v1/payments',json={})
    assert response.status_code==400


def test_security_headers_are_present():
    response=create_app(testing=True).test_client().get('/api/v1/health')
    assert response.headers['X-Frame-Options']=='DENY'
    assert 'default-src' in response.headers['Content-Security-Policy']


def test_login_contract_rejects_missing_credentials():
    assert create_app(testing=True).test_client().post('/api/v1/security/login',json={}).status_code==422
