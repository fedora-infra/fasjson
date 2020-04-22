import json
import types

from unittest import mock

from fasjson.web.app import app, errors


def test_app_gss_forbidden_error(client, gss_env):
    rv = client.get("/", environ_base=gss_env)
    body = json.loads(rv.data)
    expected_data = {
        "codes": {
            "maj": 851968,
            "min": 2529639107,
            "routine": 851968,
            "supplementary": None,
        }
    }

    assert rv.status_code == 403
    assert body["error"]["data"] == expected_data
    assert body["error"]["message"] == "Invalid credentials"


def test_app_default_unauthorized_error(client, gss_env):
    with mock.patch("gssapi.Credentials") as M:
        M.return_value = types.SimpleNamespace(lifetime=0)
        rv = client.get("/", environ_base=gss_env)
    body = json.loads(rv.data)

    assert rv.status_code == 401
    assert body["error"]["data"] is None
    assert body["error"]["message"] == "Credential lifetime has expired"


def test_app_default_notfound_error(client, gss_env):
    with mock.patch("gssapi.Credentials") as M:
        M.return_value = types.SimpleNamespace(lifetime=10)
        rv = client.get("/notfound", environ_base=gss_env)
    body = json.loads(rv.data)

    assert rv.status_code == 404
    assert body["error"]["data"] == {"method": "GET", "path": "/notfound"}
    assert body["error"]["message"] == "resource not found"


def test_app_default_internal_error(client, gss_env):
    @app.route("/500")
    def fivehundred():
        x = []
        return x[10]

    with mock.patch("gssapi.Credentials") as M:
        M.return_value = types.SimpleNamespace(lifetime=10)
        rv = client.get("/500", environ_base=gss_env)
    body = json.loads(rv.data)

    assert rv.status_code == 500
    assert body["error"]["data"] == {
        "exception": "list index out of range",
        "method": "GET",
        "path": "/500",
    }
    assert body["error"]["message"] == "unexpected internal error"


def test_app_registered_error(client, gss_env):
    @app.route("/")
    def root():
        raise errors.WebApiError("forbidden", 403, data={"foo": "bar"})

    with mock.patch("gssapi.Credentials") as M:
        M.return_value = types.SimpleNamespace(lifetime=10)
        rv = client.get("/", environ_base=gss_env)
    body = json.loads(rv.data)

    assert rv.status_code == 403
    assert body["error"]["data"] == {"foo": "bar"}
    assert body["error"]["message"] == "forbidden"
