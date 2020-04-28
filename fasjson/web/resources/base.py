from flask_restx import Namespace as RestXNamespace


class Namespace(RestXNamespace):
    def marshal_with(self, *args, **kwargs):
        kwargs.setdefault("envelope", "result")
        return super().marshal_with(*args, **kwargs)
