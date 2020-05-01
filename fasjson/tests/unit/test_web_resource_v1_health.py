import json

import ldap


def test_live_success(anon_client):
    rv = anon_client.get("/healthz/v1/live/")
    expected = {"result": {"status": "OK"}}
    assert 200 == rv.status_code
    assert expected == json.loads(rv.data)


def test_ready_success(anon_client, mocker):
    bind_mock = mocker.patch("ldap.ldapobject.SimpleLDAPObject.simple_bind_s")
    bind_mock.return_value = None
    rv = anon_client.get("/healthz/v1/ready/")
    res = json.loads(rv.data)
    expected = {"result": {"status": "OK"}}

    assert 200 == rv.status_code
    assert expected == res


def test_ready_error(anon_client, mocker):
    mocker.patch(
        "ldap.ldapobject.SimpleLDAPObject.simple_bind_s",
        side_effect=ldap.SERVER_DOWN,
    )
    rv = anon_client.get("/healthz/v1/ready/")
    res = json.loads(rv.data)
    expected = {"result": {"status": "NOT OK"}}

    assert 503 == rv.status_code
    assert expected == res
