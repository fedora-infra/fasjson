import pytest
from flask import g
from werkzeug.exceptions import Unauthorized

from fasjson.web.app import app
from fasjson.web.utils.ldap import ldap_client


def test_ldap_client(mocker, gss_user, app_config):
    get_client = mocker.patch("fasjson.web.utils.ldap.get_client")
    with app.test_request_context("/v1/me/"):
        app.preprocess_request()
        g.gss_name = "dummy"
        ldap_client()
    get_client.assert_called_with(
        "ldap://ipa.example.test",
        basedn="dc=example,dc=test",
        login="dummy",
        timeout=30,
    )


def test_ldap_client_anon(mocker, gss_user, app_config):
    get_client = mocker.patch("fasjson.web.utils.ldap.get_client")
    with app.test_request_context("/v1/me/"):
        app.preprocess_request()
        g.gss_name = None
        with pytest.raises(Unauthorized):
            ldap_client()
    get_client.assert_not_called()
