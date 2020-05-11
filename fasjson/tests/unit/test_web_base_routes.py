import json

import ldap


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


def test_live_success(anon_client):
    rv = anon_client.get("/healthz/live")
    assert 200 == rv.status_code
    assert b"OK" in rv.data


def test_ready_success(anon_client, mocker):
    bind_mock = mocker.patch("ldap.ldapobject.SimpleLDAPObject.simple_bind_s")
    # a successful return value is None, so we don't want simple_bind_s to complain
    bind_mock.return_value = None
    rv = anon_client.get("/healthz/ready")

    assert 200 == rv.status_code
    assert b"OK" in rv.data


def test_ready_error(anon_client, mocker):
    mocker.patch(
        "ldap.ldapobject.SimpleLDAPObject.simple_bind_s",
        side_effect=ldap.SERVER_DOWN,
    )
    rv = anon_client.get("/healthz/ready")

    assert 503 == rv.status_code
    assert b"LDAP server is down" in rv.data
