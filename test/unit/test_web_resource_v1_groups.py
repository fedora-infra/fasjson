from unittest import mock
import json
import types

import pytest

from fasjson.web import app


def test_groups_success(client, gss_env):
    mocked = [
        ('', {'cn': [b'admins']},),
        ('', {'cn': [b'ipausers']},),
        ('', {'cn': [b'editors']},),
        ('', {'cn': [b'trust admins']},),
    ]
    with mock.patch('gssapi.Credentials') as G, mock.patch('ldap.initialize') as L:
        G.return_value = types.SimpleNamespace(lifetime=10)
        L.return_value = types.SimpleNamespace(
            sasl_interactive_bind_s=lambda s, n: '',
            search_s=lambda a, b, c, d: mocked)
        rv = client.get('/v1/groups', environ_base=gss_env)

    expected = {"result":{"data":["admins","ipausers","editors","trust admins"]}}

    assert 200 == rv.status_code
    assert expected == json.loads(rv.data)


def test_groups_error_notfound(client, gss_env):
    with mock.patch('gssapi.Credentials') as G, mock.patch('ldap.initialize') as L:
        G.return_value = types.SimpleNamespace(lifetime=10)
        L.return_value = types.SimpleNamespace(
            sasl_interactive_bind_s=lambda s, n: '',
            search_s=lambda a, b, c, d: [])
        rv = client.get('/v1/groups', environ_base=gss_env)

    assert 404 == rv.status_code
    assert '0 groups found' == json.loads(rv.data)['error']['message']


def test_groups_error(client, gss_env):
    with mock.patch('gssapi.Credentials') as G, mock.patch('ldap.initialize') as L:
        G.return_value = types.SimpleNamespace(lifetime=10)
        rv = client.get('/v1/groups', environ_base=gss_env)

    assert 404 == rv.status_code
    assert '0 groups found' == json.loads(rv.data)['error']['message']


def test_group_members_success(client, gss_env):
    mocked = [
        ('', {'uid': [b'admin']},)
    ]
    with mock.patch('gssapi.Credentials') as G, mock.patch('ldap.initialize') as L:
        G.return_value = types.SimpleNamespace(lifetime=10)
        L.return_value = types.SimpleNamespace(
            sasl_interactive_bind_s=lambda s, n: '',
            search_s=lambda a, b, c, d: mocked)
        rv = client.get('/v1/groups/admins/members', environ_base=gss_env)

    expected = {"result":{"data":["admin"]}}

    assert 200 == rv.status_code
    assert expected == json.loads(rv.data)


def test_group_members_error(client, gss_env):
    with mock.patch('gssapi.Credentials') as G, mock.patch('ldap.initialize') as L:
        G.return_value = types.SimpleNamespace(lifetime=10)
        L.return_value = types.SimpleNamespace(
            sasl_interactive_bind_s=lambda s, n: '',
            search_s=lambda a, b, c, d: None)
        rv = client.get('/v1/groups/editors/members', environ_base=gss_env)
    res = json.loads(rv.data)
    
    assert 404 == rv.status_code
    assert '0 members found' == res['error']['message']
    assert {'group': 'editors'} == res['error']['data']
