import json

from flask import Response

from . import errors


class ApiResponse(Response):
    charset = 'utf-8'
    default_status = 200
    default_mimetype = 'application/json'
