import json

from src.fasjson.web import errors


def test_webapierror_as_dict():
	err = errors.WebApiError('foobar', 404)
	assert {'error': {'data': None, 'message': 'foobar'}} == err.as_dict()


def test_webapierror_as_dict_full():
	err = errors.WebApiError('foobar', 404, data={'foo': 'bar'})
	assert {'error': {'data': {'foo': 'bar'}, 'message': 'foobar'}} == err.as_dict()


def test_webapierror_as_json():
	err = errors.WebApiError('foobar', 404, data={'foo': 'bar'})
	jsonstr = err.as_json()
	assert {'error': {'data': {'foo': 'bar'}, 'message': 'foobar'}} == json.loads(jsonstr)