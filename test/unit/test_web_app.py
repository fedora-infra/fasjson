import json

from src.fasjson.web import app, errors


def test_app_default_notfound_error():
    client = app.app.test_client()
    rv = client.get('/notfound')
    body = json.loads(rv.data)

    assert rv.status_code == 404
    assert body['data'] == {'method': 'GET', 'path': '/notfound'}
    assert body['message'] == 'resource not found'


def test_app_default_internal_error():
    client = app.app.test_client()
    @app.app.route('/500')
    def fivehundred():
        x = []
        return x[10]

    rv = client.get('/500')
    body = json.loads(rv.data)

    assert rv.status_code == 500
    assert body['data'] == {'exception': 'list index out of range', 'method': 'GET', 'path': '/500'}
    assert body['message'] == 'unexpected internal error'


def test_app_registered_error():
    client = app.app.test_client()
    @app.app.route('/')
    def root():
        raise errors.WebApiError('forbidden', 403, data={'foo': 'bar'})
    rv = client.get('/')
    body = json.loads(rv.data)

    assert rv.status_code == 403
    assert body['data'] == {'foo': 'bar'}
    assert body['message'] == 'forbidden'


