import os
import json
import types

import pytest
from flask_restx import abort

from fasjson.web.app import create_app


def test_app_gss_forbidden_error(client):
    rv = client.get("/")
    body = json.loads(rv.data)
    expected_codes = {
        "maj": 851_968,
        "min": 2_529_639_107,
        "routine": 851_968,
        "supplementary": None,
    }

    assert rv.status_code == 403
    assert body == {"message": "Invalid credentials", "codes": expected_codes}


def test_app_default_unauthorized_error(client, mocker):
    creds_factory = mocker.patch("gssapi.Credentials")
    creds_factory.return_value = types.SimpleNamespace(lifetime=0)
    rv = client.get("/")
    body = json.loads(rv.data)

    assert rv.status_code == 401
    assert body == {"message": "Credential lifetime has expired"}


def test_app_default_notfound_error(client, gss_user):
    rv = client.get("/notfound")
    body = json.loads(rv.data)

    assert rv.status_code == 404
    assert body.get("message") is not None


def test_app_default_internal_error(client, gss_user):
    @client.application.route("/500")
    def fivehundred():
        x = []
        return x[10]

    # Don't catch the exception in the testing framework
    client.application.config["TESTING"] = False

    rv = client.get("/500")
    body = json.loads(rv.data)

    assert rv.status_code == 500
    assert body.get("message") is not None


def test_app_registered_error(client, gss_user):
    @client.application.route("/403")
    def forbidden():
        abort(403, "forbidden", foo="bar")

    rv = client.get("/403")
    body = json.loads(rv.data)

    assert rv.status_code == 403
    assert body == {"foo": "bar", "message": "forbidden"}


def test_webserver_error(anon_client):
    for code in (401, 403, 500):
        rv = anon_client.get(f"/errors/{code}")
        assert rv.status_code == code
        body = json.loads(rv.data)
        assert "message" in body


@pytest.fixture
def temp_config(tmpdir):
    config_path = os.path.join(tmpdir, "testing.cfg")
    with open(config_path, "w") as config_file:
        config_file.write("DUMMY = 'dummy'\n")
    os.environ["FASJSON_CONFIG_PATH"] = config_path
    yield
    del os.environ["FASJSON_CONFIG_PATH"]


def test_configuration_file(temp_config, app):
    with app.test_request_context("/"):
        assert app.config.get("DUMMY") == "dummy"


def test_logging_config(mocker):
    dictConfig = mocker.patch("fasjson.web.app.dictConfig")
    logging_config = {
        "version": 1,
        "root": {"level": "DEBUG", "handlers": []},
    }
    create_app(config={"LOGGING": logging_config})
    dictConfig.assert_called_with(logging_config)
