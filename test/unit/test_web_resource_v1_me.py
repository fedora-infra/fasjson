import json
import types
from unittest import mock

import pytest
import gssapi
import ldap

from src.fasjson.web import app


def test_me_success(client, gss_env):
    r = 'dn: krbprincipalname=http/fasjson.example.test@example.test,cn=services,cn=accounts,dc=example,dc=test'
    with mock.patch('gssapi.Credentials') as G, mock.patch('ldap.initialize') as L:
        G.return_value = types.SimpleNamespace(lifetime=10)
        L.return_value = types.SimpleNamespace(
            sasl_interactive_bind_s=lambda s, n: '',
            whoami_s=lambda: r)
        rv = client.get('/v1/me', environ_base=gss_env)
    expected = {
        'result': {
            'raw': r,
            'info': {
                'krbprincipalname': 'http/fasjson.example.test@example.test',
                'cn': ['services', 'accounts'],
                'dc': ['example', 'test']
            }
        }
    }

    assert 200 == rv.status_code
    assert expected == json.loads(rv.data)


def test_me_error(client, gss_env):
    with mock.patch('gssapi.Credentials') as G:
        G.return_value = types.SimpleNamespace(lifetime=10)
        rv = client.get('/v1/me', environ_base=gss_env)
    res = json.loads(rv.data)
    
    assert 500 == rv.status_code
    assert 'LDAP local error' == res['error']['message']
    assert 'Unspecified GSS failure' in res['error']['data']['exception']
