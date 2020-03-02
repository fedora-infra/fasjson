from .base import BaseResource
from fasjson.web import errors


class Me(BaseResource):
    def get(self):
        raise errors.WebApiError('method not implemented', 405, data={'reason': 'method not implemented'})
