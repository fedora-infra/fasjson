import json
import types

from flask_restx import abort

from fasjson.web.app import app


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


def test_root_anonymous(anon_client):
    rv = anon_client.get("/")
    body = json.loads(rv.data)

    assert rv.status_code == 200
    expected = {
        "apis": [
            {
                "docs": "http://localhost/docs/v1/",
                "specs": "http://localhost/specs/v1.json",
                "uri": "http://localhost/v1/",
                "version": 1,
            }
        ],
        "message": "Welcome to FASJSON",
    }
    assert body == expected


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
    @app.route("/500")
    def fivehundred():
        x = []
        return x[10]

    # Don't catch the exception in the testing framework
    app.config["TESTING"] = False

    rv = client.get("/500")
    body = json.loads(rv.data)

    assert rv.status_code == 500
    assert body.get("message") is not None


def test_app_registered_error(client, gss_user):
    @app.route("/403")
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
