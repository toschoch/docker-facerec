def test_config(client):
    r = client.get('config')
    assert r.status_code == 200
    assert r.json == {'threshold': 0.6}

    r = client.get('config/notexisting')
    assert r.status_code == 404
    assert r.json == {'message': "No configuration parameter 'notexisting' found"}

def test_threshold(client):
    r = client.get('config/threshold')
    assert r.status_code == 200
    assert r.json == 0.6

    r = client.patch('config/threshold')
    assert r.status_code == 400
    assert r.json == {'message': {'value': 'threshold must be a float value'}}

    r = client.patch('config/threshold', data={'value':'a'})
    assert r.status_code == 400
    assert r.json == {'message': {'value': 'threshold must be a float value'}}

    r = client.patch('config/threshold', data={'value':0.61})
    assert r.status_code == 200
    assert r.json == 0.61

    r = client.get('config/threshold')
    assert r.status_code == 200
    assert r.json == 0.61
