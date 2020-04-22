import json

from .response import ApiResponse as Response
from werkzeug.exceptions import HTTPException


class WebApiError(HTTPException):
    """
    HTTP exception to be used across the web api.

    It inherits werkzeug HTTPException exception class.
    """

    def __init__(self, message, code, data=None):
        super(WebApiError, self).__init__(message)
        self.code = code
        self.message = message
        self.extra = data

    def as_dict(self):
        """
        Returns exception data in dict format.
        """
        return {"error": {"message": self.message, "data": self.extra}}

    def as_json(self) -> str:
        """
        Returns the json string reprsentation of this object.
        """
        return json.dumps(self.as_dict(), sort_keys=True, indent=4)

    def get_description(self, environ=None):
        """
        Return the error message as its description.
        """
        return self.message

    def get_headers(self, environ=None):
        """
        Returns error http headers.
        """
        return [("Content-Type", "application/json;charset=utf-8")]

    def get_body(self, environ=None):
        """
        Return the error http body as a string.
        """
        return self.as_json()

    def get_response(self, environ=None):
        return Response(
            self.get_body(environ), self.code, self.get_headers(environ)
        )
