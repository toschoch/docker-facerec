import base64
import utils
import numpy as np
import json
from PIL import Image
import glob
from io import BytesIO


def test_identify(client):
    image = Image.open(glob.glob('data/*.png')[0]).convert('RGB')
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    # encode face code and send to identify
    payload = {'image': base64.b64encode(buffer.getvalue()).decode('ascii')}
    r = client.post('image/identify', data=json.dumps(payload), content_type='application/json')

    assert r.status_code == 200
    assert len(r.json)==1
    # code = np.frombuffer(base64.b64decode(r.json[0]['person']['code']))
    # print(code)

def test_teach(client):

    image = Image.open(glob.glob('data/*.png')[0]).convert('RGB')
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    # encode face code and send to identify
    payload = {'image': base64.b64encode(buffer.getvalue()).decode('ascii')}
    r = client.post('image/identify', data=json.dumps(payload), content_type='application/json')

    code = np.frombuffer(base64.b64decode(r.json[0]['person']['code']))

    # encode face code and send to identify
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    payload = {'image': base64.b64encode(buffer.getvalue()).decode('ascii')}
    r = client.post('image/teach',data=json.dumps(payload),content_type='application/json')

    assert r.status_code == 400
    assert r.json['message'] == 'either ID or NAME must be specified!'

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    payload = {'image': base64.b64encode(buffer.getvalue()).decode('ascii'),'id':1}
    r = client.post('image/teach',data=json.dumps(payload),content_type='application/json')

    assert r.status_code == 200

    r = client.get('faces')
    assert len(r.json) == 1

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    payload = {'image': base64.b64encode(buffer.getvalue()).decode('ascii'), 'name': 'Mickey Mouse'}
    r = client.post('image/teach', data=json.dumps(payload), content_type='application/json')

    assert r.status_code == 200
    code2 = np.frombuffer(base64.b64decode(r.json['person']['code']))
    assert np.all(code == code2)

    assert r.json['person']['nmeans'] == '3.0'

    r = client.get('faces')
    assert len(r.json)==1
