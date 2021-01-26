import pytest
from fasjson.web.utils.ipa import ldap_client, rpc_client
from flask import g
from werkzeug.exceptions import Unauthorized


def test_ldap_client(mocker, gss_user, app):
    get_client = mocker.patch("fasjson.web.utils.ipa.get_client")
    with app.test_request_context("/v1/me/"):
        app.preprocess_request()
        g.gss_creds = object()
        g.username = "dummy"
        ldap_client()
    get_client.assert_called_with(
        "ldap://ipa.example.test",
        basedn="dc=example,dc=test",
        login="dummy",
        timeout=30,
    )


def test_ldap_client_anon(mocker, gss_user, app):
    get_client = mocker.patch("fasjson.web.utils.ipa.get_client")
    with app.test_request_context("/v1/me/"):
        app.preprocess_request()
        g.gss_creds = None
        with pytest.raises(Unauthorized):
            ldap_client()
    get_client.assert_not_called()


def test_rpc_client(mocker, gss_user, app):
    ClientMeta = mocker.patch("fasjson.web.utils.ipa.ClientMeta")
    client = mocker.Mock()
    ClientMeta.return_value = client
    with app.test_request_context("/v1/me/"):
        app.preprocess_request()
        g.gss_creds = object()
        rpc_client()
    ClientMeta.assert_called_once_with(
        "ipa.example.test", verify_ssl=app.config["FASJSON_IPA_CA_CERT_PATH"]
    )
    client.login_kerberos.assert_called_once_with()


def test_rpc_client_anon(mocker, gss_user, app):
    ClientMeta = mocker.patch("fasjson.web.utils.ipa.ClientMeta")
    with app.test_request_context("/v1/me/"):
        app.preprocess_request()
        g.gss_creds = None
        with pytest.raises(Unauthorized):
            rpc_client()
    ClientMeta.assert_not_called()
