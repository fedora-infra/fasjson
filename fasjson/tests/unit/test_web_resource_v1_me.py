import json
import types
from unittest import mock

from pytest_mock import mocker


def test_me_success(client, gss_env):
    r = (
        "dn: krbprincipalname=http/fasjson.example.test@example.test,"
        "cn=services,cn=accounts,dc=example,dc=test"
    )
    G = mocker.patch("gssapi.Credentials")
    L = mocker.patch("ldap.initialize")
    G.return_value = types.SimpleNamespace(lifetime=10)
    L.return_value = types.SimpleNamespace(
        protocol_version=3,
        set_option=lambda a, b: a,
        sasl_interactive_bind_s=lambda s, n: "",
        whoami_s=lambda: r,
    )

    rv = client.get("/v1/me", environ_base=gss_env)
    expected = {
        "result": {
            "raw": r,
            "info": {
                "krbprincipalname": "http/fasjson.example.test@example.test",
                "cn": ["services", "accounts"],
                "dc": ["example", "test"],
            },
        }
    }

    assert 200 == rv.status_code
    assert expected == json.loads(rv.data)


def test_me_error(client, gss_env):
    G = mock.patch("gssapi.Credentials")
    G.return_value = types.SimpleNamespace(lifetime=10)
    rv = client.get("/v1/me", environ_base=gss_env)
    res = json.loads(rv.data)
    expected = {
        "error": {
            "data": {
                "codes": {
                    "maj": 851968,
                    "min": 2529639107,
                    "routine": 851968,
                    "supplementary": None,
                }
            },
            "message": "Invalid credentials",
        }
    }

    assert 403 == rv.status_code
    assert "Invalid credentials" == res["error"]["message"]
    assert expected == res
