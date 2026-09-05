from backend.app import create_app


def test_management_catalog_contracts():
    client=create_app(testing=True).test_client()
    assert client.get('/api/v1/categories').status_code==200
    assert client.post('/api/v1/categories',json={'code':'BEB','name':'Bebidas'}).status_code==201
    assert client.post('/api/v1/suppliers',json={'code':'SUP1','name':'Proveedor Uno','email':'ventas@example.com'}).status_code==201
    assert client.post('/api/v1/locations',json={'code':'MAIN','name':'Sucursal principal'}).status_code==201


def test_management_security_contracts():
    client=create_app(testing=True).test_client()
    assert client.get('/api/v1/security/users').status_code==200
    assert client.get('/api/v1/security/roles').status_code==200
    response=client.put('/api/v1/security/settings',json={'business_name':'Comercio Inteligente','tax_id':'0999999999','currency':'USD','timezone':'America/Guayaquil','low_stock_threshold':5,'expiry_warning_days':30})
    assert response.status_code==200
    assert client.get('/api/v1/security/settings').get_json()['data']['currency']=='USD'


def test_custom_role_contract():
    client=create_app(testing=True).test_client()
    response=client.post('/api/v1/security/roles',json={'code':'stock_viewer','name':'Consulta de inventario','permissions':['inventory.read','products.read']})
    assert response.status_code==201
    assert response.get_json()['data']['permissions']==['inventory.read','products.read']
