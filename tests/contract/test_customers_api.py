from backend.app import create_app
def test_customer_requires_name():
    r=create_app(testing=True).test_client().post('/api/v1/customers',json={'email':'x@example.com'})
    assert r.status_code==422
def test_consent_validates_channel():
    r=create_app(testing=True).test_client().post('/api/v1/customers/000000000000000000000000/consents',json={'channel':'fax','granted':True})
    assert r.status_code==422
