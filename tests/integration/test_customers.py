from backend.app import create_app
from backend.db import get_db


def test_customer_consent_and_birthday_coupon():
    db=get_db();assert db.name.endswith('_test')
    for n in ('customers','customer_consents','coupons'):db[n].delete_many({})
    c=create_app(testing=True).test_client();created=c.post('/api/v1/customers',json={'name':'Ana Leal','email':'ANA@example.com','birthday':'1990-09-03'})
    assert created.status_code==201;cid=created.json['data']['id']
    assert c.post(f'/api/v1/customers/{cid}/consents',json={'channel':'email','granted':True}).status_code==201
    coupon=c.post(f'/api/v1/customers/{cid}/birthday-coupon')
    assert coupon.status_code==201 and coupon.json['data']['code'].startswith('CUM-')
