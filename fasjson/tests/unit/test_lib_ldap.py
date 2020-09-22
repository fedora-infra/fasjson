from fasjson.lib.ldap import get_client


def test_get_client(mocker):
    LDAP = mocker.patch("fasjson.lib.ldap.LDAP")
    LDAP.return_value = object()
    client = get_client("ldap://", "dc=example,dc=test", "dummy")
    LDAP.assert_called_once_with("ldap://", "dc=example,dc=test")
    assert client == LDAP.return_value
