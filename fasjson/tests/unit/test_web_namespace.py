import json

import ldap
from python_freeipa.exceptions import BadRequest


def test_schema(client, gss_user):
    rv = client.get("/specs/v1.json")
    assert rv.status_code == 200
    body = json.loads(rv.data)
    assert body["basePath"] == "/v1"
    assert body["info"]["title"] == "FAS-JSON"
    assert body["info"]["version"] == "1.0"
    assert body["swagger"] == "2.0"


def test_ldap_local_error(client, gss_user, mocker):
    mocker.patch(
        "fasjson.web.resources.me.ldap_client", side_effect=ldap.LOCAL_ERROR
    )
    rv = client.get("/v1/me/")
    assert rv.status_code == 500
    body = json.loads(rv.data)
    assert body["message"] == "LDAP local error"
    assert body["source"] == "LDAP"


def test_ldap_server_error(client, gss_user, mocker):
    mocker.patch(
        "fasjson.web.resources.me.ldap_client", side_effect=ldap.SERVER_DOWN
    )
    rv = client.get("/v1/me/")
    assert rv.status_code == 500
    body = json.loads(rv.data)
    assert body["message"] == "LDAP server is down"
    assert body["source"] == "LDAP"


def test_rpc_bad_request(client, gss_user, mocker):
    mocker.patch(
        "fasjson.web.resources.certs.rpc_client",
        side_effect=BadRequest(message="dummy message", code=42),
    )
    rv = client.get("/v1/certs/1/")
    assert rv.status_code == 400
    body = json.loads(rv.data)
    assert body["message"] == "dummy message"
    assert body["code"] == 42
    assert body["source"] == "RPC"
