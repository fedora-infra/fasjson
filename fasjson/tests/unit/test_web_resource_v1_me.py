import json


def test_me_user_success(client, gss_user, mock_ldap_client):
    r = {
        "dn": "uid=dummy,cn=users,cn=accounts,dc=example,dc=test",
        "username": "dummy",
    }
    mock_ldap_client("fasjson.web.resources.me", whoami=lambda: r)

    rv = client.get("/v1/me/")
    expected = {
        "result": {
            "dn": r["dn"],
            "username": "dummy",
            "service": None,
            "uri": "http://localhost/v1/users/dummy/",
        }
    }

    assert 200 == rv.status_code
    assert expected == json.loads(rv.data)


def test_me_service_success(client, gss_user, mock_ldap_client):
    r = {
        "dn": (
            "krbprincipalname=test/fasjson.example.test@example.test,"
            "cn=services,cn=accounts,dc=example,dc=test"
        ),
        "service": "test/fasjson.example.test",
    }
    mock_ldap_client("fasjson.web.resources.me", whoami=lambda: r)

    rv = client.get("/v1/me/")
    expected = {
        "result": {
            "dn": r["dn"],
            "username": None,
            "service": "test/fasjson.example.test",
            "uri": None,
        }
    }

    assert 200 == rv.status_code
    assert expected == json.loads(rv.data)


def test_me_error(client, gss_env):
    rv = client.get("/v1/me/")
    res = json.loads(rv.data)
    expected = {
        "codes": {
            "maj": 851968,
            "min": 2529639107,
            "routine": 851968,
            "supplementary": None,
        },
        "message": "Invalid credentials",
    }

    assert 403 == rv.status_code
    # assert "Invalid credentials" == res["error"]["message"]
    assert expected == res
