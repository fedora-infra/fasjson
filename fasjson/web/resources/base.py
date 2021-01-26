from functools import wraps

from flask_restx import Namespace as RestXNamespace
from flask_restx.utils import merge, unpack

from ..utils.pagination import paged_marshal


class Namespace(RestXNamespace):
    def marshal_with(self, fields, *args, **kwargs):
        if not isinstance(fields, dict):
            return self.marshal_with_field(fields, *args, **kwargs)
        kwargs.setdefault("envelope", "result")
        return super().marshal_with(fields, *args, **kwargs)

    def paged_marshal_with(self, model, description=None, **marshal_kwargs):
        """
        A decorator to call paged_marshal. See Namespace.marshal_with for reference.
        """

        def decorator(func):
            full_marshal_kwargs = marshal_kwargs.copy()
            full_marshal_kwargs["envelope"] = "result"
            doc = {
                "responses": {
                    "200": (description, [model], full_marshal_kwargs)
                },
                # Mask values can't be determined outside app context
                "__mask__": marshal_kwargs.get("mask", True),
            }
            func.__apidoc__ = merge(getattr(func, "__apidoc__", {}), doc)

            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return paged_marshal(
                    result, model, ordered=self.ordered, **marshal_kwargs
                )

            return wrapper

        return decorator

    def marshal_with_field(self, field, *args, description=None):
        # Sadly we can't use flask_restx.marshalling.marshal_with_field because it does not
        # support envelopes.
        if isinstance(field, type):
            field = field()

        def decorator(func):
            doc = {
                "responses": {
                    "200": (description, field, {"envelope": "result"})
                },
            }
            func.__apidoc__ = merge(getattr(func, "__apidoc__", {}), doc)

            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if isinstance(result, tuple):
                    data, code, headers = unpack(result)
                    return {"result": field.format(data)}, code, headers
                return {"result": field.format(result)}

            return wrapper

        return decorator

    def add_resource(self, resource, *urls, **kwargs):
        """Each API endpoint can return 401 if authentication is not successful."""
        self.response(401, "Unauthorized. You need to be logged in.")(
            resource
        )
        return super().add_resource(resource, *urls, **kwargs)
