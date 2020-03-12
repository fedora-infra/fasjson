import json
import types

import pytest

from fasjson.web import app


def test_groups_success(client, gss_env, mocker):
    data = ['admins', 'ipausers', 'editors', 'trust admins']
    G = mocker.patch('gssapi.Credentials')
    L = mocker.patch('fasjson.lib.ldaputils.singleton')
    G.return_value = types.SimpleNamespace(lifetime=10)
    L.return_value = types.SimpleNamespace(
        get_groups=lambda size, cookie: ('2', len(data), b'0', data)
    )
    rv = client.get('/v1/groups', environ_base=gss_env)

    expected = { 
        'result':{
            'data': data,
            'size': len(data)
        }
    }

    assert 200 == rv.status_code
    assert expected == json.loads(rv.data)


def test_groups_error_notfound(client, gss_env, mocker):
    G = mocker.patch('gssapi.Credentials')
    L = mocker.patch('fasjson.lib.ldaputils.singleton')
    G.return_value = types.SimpleNamespace(lifetime=10)
    L.return_value = types.SimpleNamespace(
        get_groups=lambda size, cookie:[None, 0, None, []])
    rv = client.get('/v1/groups', environ_base=gss_env)

    assert 404 == rv.status_code
    assert '0 groups found' == json.loads(rv.data)['error']['message']


def test_groups_error(client, gss_env, mocker):
    G = mocker.patch('gssapi.Credentials')
    G.return_value = types.SimpleNamespace(lifetime=10)
    rv = client.get('/v1/groups', environ_base=gss_env)

    assert 500 == rv.status_code
    assert 'Can\'t contact LDAP server' in json.loads(rv.data)['error']['data']['exception']


def test_group_members_success(client, gss_env, mocker):
    data = ['admin']
    G = mocker.patch('gssapi.Credentials')
    L = mocker.patch('fasjson.lib.ldaputils.singleton')
    G.return_value = types.SimpleNamespace(lifetime=10)
    L.return_value = types.SimpleNamespace(
        get_group_members=lambda name, size, cookie: ('2', len(data), b'0', data)
    )
    rv = client.get('/v1/groups/admins/members', environ_base=gss_env)

    expected = {
        'result': {
            'data': data,
            'size': len(data)
        }
    }

    assert 200 == rv.status_code
    assert expected == json.loads(rv.data)


def test_group_members_error(client, gss_env, mocker):
    data = []
    G = mocker.patch('gssapi.Credentials')
    G.return_value = types.SimpleNamespace(lifetime=10)
    L = mocker.patch('fasjson.lib.ldaputils.singleton')
    L.return_value = types.SimpleNamespace(
        get_group_members=lambda name, size, cookie:[None, len(data), None, data])
    rv = client.get('/v1/groups/editors/members', environ_base=gss_env)
    res = json.loads(rv.data)
    
    expected = {
        'error': {
            'data': None,
            'message': '0 groups found'
        }
    }


    assert 404 == rv.status_code
    assert expected == json.loads(rv.data)
