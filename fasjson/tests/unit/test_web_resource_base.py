import pytest
from flask_restx import fields

from fasjson.web.resources.base import Namespace


@pytest.fixture
def api():
    return Namespace("test")


def test_marshal_with_field(api):
    class TestResource:
        @api.marshal_with(fields.Boolean())
        def get(self):
            return True

    resource = TestResource()
    assert resource.get() == {"result": True}


def test_marshal_with_field_class(api):
    class TestResource:
        @api.marshal_with(fields.Boolean)
        def get(self):
            return True

    resource = TestResource()
    assert resource.get() == {"result": True}


def test_marshal_with_field_tuple_response(api):
    headers = dict()

    class TestResource:
        @api.marshal_with(fields.Boolean())
        def get(self):
            return True, 200, headers

    resource = TestResource()
    assert resource.get() == ({"result": True}, 200, headers)
