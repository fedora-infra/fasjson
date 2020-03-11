import json
import types

import pytest

from fasjson.web import app


def test_user_success(client, gss_env, mocker):
    # data1 = {
    #     "uid": [b"admin"],
    #     'sn': [b'Administrator'],
    #     "givenName": [b''],
    #     "mail": [b'admin@example.test'],
    #     "fasIRCNick": [b''],
    #     "fasLocale": [b''],
    #     "fasTimeZone": [b''],
    #     "fasGPGKeyId": None,
    #     "fasCreationTime": [b'20200309103203Z'], #%Y%m%d%H%M%SZ
    #     "nsAccountLock": [b'false'],
    # }
    data = {
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
    mocked = [
        ('', data,),
    ]
    G = mocker.patch('gssapi.Credentials')
    L = mocker.patch('fasjson.lib.ldaputils.singleton')
    G.return_value = types.SimpleNamespace(lifetime=10)
    L.return_value = types.SimpleNamespace(
        get_user=lambda u: data)
    
    rv = client.get('/v1/users/admin', environ_base=gss_env)

    assert 200 == rv.status_code
    assert {'result': data} == json.loads(rv.data)



def test_user_error(client, gss_env, mocker):
    G = mocker.patch('gssapi.Credentials')
    L = mocker.patch('fasjson.lib.ldaputils.singleton')
    G.return_value = types.SimpleNamespace(lifetime=10)
    L.return_value = types.SimpleNamespace(
        get_user=lambda u: None)

    rv = client.get('/v1/users/admin', environ_base=gss_env)
    res = json.loads(rv.data)

    assert 404 == rv.status_code
    assert 'user not found' == res['error']['message']
    assert {'username': 'admin'} == res['error']['data']
