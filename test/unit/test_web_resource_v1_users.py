import json
import types

import pytest
from unittest import mock

from fasjson.web import app


def test_user_success(client, gss_env):
    data = {
        "uid": [b"admin"],
        'sn': [b'Administrator'],
        "givenName": [b''],
        "mail": [b'admin@example.test'],
        "fasIRCNick": [b''],
        "fasLocale": [b''],
        "fasTimeZone": [b''],
        "fasGPGKeyId": None,
        "fasCreationTime": [b'20200309103203Z'], #%Y%m%d%H%M%SZ
        "nsAccountLock": [b'false'],
    }
    mocked = [
        ('', data,),
    ]
    with mock.patch('gssapi.Credentials') as G, mock.patch('ldap.initialize') as L:
        G.return_value = types.SimpleNamespace(lifetime=10)
        L.return_value = types.SimpleNamespace(
            sasl_interactive_bind_s=lambda s, n: '',
            search_s=lambda a, b, c, d: mocked)
        rv = client.get('/v1/users/admin', environ_base=gss_env)

    expected = {
        "result": {
            "creationts": 'Mon, 09 Mar 2020 10:32:03 GMT',
            "givenname": '',
            "gpgkeyids": None,
            "ircnick": '',
            "locale": '',
            "locked": False,
            "login": "admin",
            "mails": ['admin@example.test'],
            "surename":"Administrator",
            "timezone": ''
        }
    }

    assert 200 == rv.status_code
    assert expected == json.loads(rv.data)



def test_user_error(client, gss_env):
    with mock.patch('gssapi.Credentials') as G, mock.patch('ldap.initialize') as L:
        G.return_value = types.SimpleNamespace(lifetime=10)
        L.return_value = types.SimpleNamespace(
            sasl_interactive_bind_s=lambda s, n: '',
            search_s=lambda a, b, c, d: None)
        rv = client.get('/v1/users/admin', environ_base=gss_env)
    res = json.loads(rv.data)

    assert 404 == rv.status_code
    assert 'user not found' == res['error']['message']
    assert {'username': 'admin'} == res['error']['data']
