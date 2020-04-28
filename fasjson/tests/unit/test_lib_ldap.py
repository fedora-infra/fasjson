import pytest

from fasjson.lib.ldap import get_client, __ldap


@pytest.fixture
def cleanup_cache():
    yield
    __ldap.clear()


def test_reuse(mocker, cleanup_cache):
    LDAP = mocker.patch("fasjson.lib.ldap.LDAP")
    LDAP.side_effect = ["client1", "client2"]
    client_1 = get_client("ldap://", "dc=example,dc=test", "dummy")
    client_2 = get_client("ldap://", "dc=example,dc=test", "dummy")
    assert client_1 is client_2


def test_dont_reuse_different_users(mocker, cleanup_cache):
    LDAP = mocker.patch("fasjson.lib.ldap.LDAP")
    LDAP.side_effect = ["client1", "client2"]
    client_1 = get_client("ldap://", "dc=example,dc=test", "dummy-1")
    client_2 = get_client("ldap://", "dc=example,dc=test", "dummy-2")
    assert client_1 is not client_2
