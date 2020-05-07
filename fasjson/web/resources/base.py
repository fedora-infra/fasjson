from functools import wraps

from flask_restx import Namespace as RestXNamespace
from flask_restx.utils import merge

from ..utils.pagination import paged_marshal


class Namespace(RestXNamespace):
    def marshal_with(self, *args, **kwargs):
        kwargs.setdefault("envelope", "result")
        return super().marshal_with(*args, **kwargs)

    def paged_marshal_with(
        self, model, endpoint, description=None, **marshal_kwargs
    ):
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
                    result,
                    model,
                    endpoint,
                    ordered=self.ordered,
                    **marshal_kwargs
                )

            return wrapper

        return decorator

    def add_resource(self, resource, *urls, **kwargs):
        """Each API endpoint can return 401 if authentication is not successful."""
        self.response(401, "Unauthorized. You need to be logged in.")(
            resource
        )
        return super().add_resource(resource, *urls, **kwargs)
