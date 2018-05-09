import base64
import numpy as np
import json
from utils import extract_facecode

def test_faces(client):
    r = client.get('faces')
    assert r.status_code == 200
    assert len(r.json)==0

def test_identify(client):
    code = np.random.rand(128)

    # encode face code and send to identify
    payload = {'code': base64.b64encode(code.tobytes()).decode('ascii')}
    r = client.post('facecode/identify',data=json.dumps(payload),content_type='application/json')

    assert r.status_code == 200

    code2 = extract_facecode(r)

    assert np.all(code==code2)

    r = client.get('faces')
    assert len(r.json)==1

def test_teach(client):
    code = np.random.rand(128)

    # encode face code and send to identify
    payload = {'code': base64.b64encode(code.tobytes()).decode('ascii'),}
    r = client.post('facecode/teach',data=json.dumps(payload),content_type='application/json')

    assert r.status_code == 400
    assert r.json['message'] == 'either ID or NAME must be specified!'

    payload = {'code': base64.b64encode(code.tobytes()).decode('ascii'),'id':1}
    r = client.post('facecode/teach',data=json.dumps(payload),content_type='application/json')

    assert r.status_code == 400
    assert r.json['message'] == 'face unknown and no name is specified! Specify a name...'

    r = client.get('faces')
    assert len(r.json) == 0

    payload = {'code': base64.b64encode(code.tobytes()).decode('ascii'), 'name': 'Mickey Mouse'}
    r = client.post('facecode/teach', data=json.dumps(payload), content_type='application/json')

    assert r.status_code == 200
    code2 = extract_facecode(r)
    assert np.all(code == code2)

    r = client.get('faces')
    assert len(r.json)==1

    r = client.get('faces/1')
    assert r.json['code']==payload['code']
    assert r.json['name']==payload['name']

    r = client.patch('faces/1', data={'name':'Donald Duck'})
    r = client.get('faces/1')
    assert r.json['code'] == payload['code']
    assert r.json['name'] == 'Donald Duck'

    # delete face
    r = client.get('faces')
    assert len(r.json) == 1
    r = client.delete('faces/1')
    r = client.get('faces')
    assert len(r.json) == 0
