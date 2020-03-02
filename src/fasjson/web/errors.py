import json

import typing
from flask import Response
from werkzeug.exceptions import HTTPException


class WebApiError(HTTPException):
	"""
	HTTP exception to be used across the web api.

	It inherits werkzeug HTTPException exception class. 
	"""
	def __init__(self, message: str, code: int, data: typing.Any = None) -> None:
		super(WebApiError, self).__init__(message)
		self.code = code
		self.message = message
		self.data = data

	def as_dict(self) -> typing.Dict[str, typing.Any]:
		"""
		Returns exception data in dict format.
		"""
		return {
			'message': self.message,
			'data': self.data
		}

	def as_json(self) -> str:
		"""
		Returns the json string reprsentation of this object.
		"""
		return json.dumps(self.as_dict())

	def get_description(self, environ=None) -> str:
		"""
		Return the error message as its description.
		"""
		return self.message

	def get_headers(self, environ=None) -> typing.List[typing.Tuple[str, str]]:
		"""
		Returns error http headers.
		"""
		return [
			('Content-Type', 'application/json;charset=utf-8')
		]

	def get_body(self, environ=None) -> str:
		"""
		Return the error http body as a string.
		"""
		return self.as_json()
