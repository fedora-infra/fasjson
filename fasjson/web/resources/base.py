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
            @wraps(func)
            def wrapper(*args, **kwargs):
                doc = {
                    "responses": {"200": (description, [model], kwargs)},
                    "__mask__": kwargs.get(
                        "mask", True
                    ),  # Mask values can't be determined outside app context
                }
                func.__apidoc__ = merge(getattr(func, "__apidoc__", {}), doc)
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
