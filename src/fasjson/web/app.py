import json

import typing
from flask import Flask, Response, request, make_response
import flask_restful #type: ignore

from . import errors, resources


def output_json(data: typing.Any, code: int, headers: typing.Dict[typing.Any, typing.Any] = None):
	resp = make_response(json.dumps({'result': data}), code)
	resp.headers.extend(headers or {})
	return resp


class ApiWrapper(flask_restful.Api):
	def __init__(self, *args, **kwargs) -> None:
		super(ApiWrapper, self).__init__(*args, **kwargs)
		self.repsentations = {
			'application/json': output_json
		}


app = Flask(__name__)
api = ApiWrapper(app)

#resources
api.add_resource(resources.Me, '/me')


@app.errorhandler(404)
def handle_error_404(e):
	data = {
		'path': request.path,
		'method': request.method
	}
	e = errors.WebApiError('resource not found', 404, data=data)
	r = Response(status=e.code, mimetype='application/json')
	r.data = e.as_json()
	return r


@app.errorhandler(500)
def handle_error_500(e):
	original = getattr(e, 'original_exception', None)
	data = {
		'path': request.path,
		'method': request.method,
		'exception': str(original)
	}
	e = errors.WebApiError('unexpected internal error', 500, data=data)
	r = Response(status=e.code, mimetype='application/json')
	r.data = e.as_json()
	return r
