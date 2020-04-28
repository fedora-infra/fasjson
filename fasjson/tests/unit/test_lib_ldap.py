import types
import datetime

import pytest
from ldap.controls.pagedresults import SimplePagedResultsControl

from fasjson.lib.ldap.client import LDAP, LDAPResult


@pytest.fixture
def mock_connection(mocker):
    conn_factory = mocker.patch("ldap.ldapobject.ReconnectLDAPObject")
    return_value = types.SimpleNamespace(
        protocol_version=3,
        set_option=lambda a, b: a,
        search_ext=lambda *a, **kw: 1,
        # sasl_interactive_bind_s=lambda s, n: "",
        sasl_gssapi_bind_s=lambda authz_id: "",
    )
    conn_factory.return_value = return_value
    yield return_value


def _single_page_result_factory(result):
    def _result(msgid, resp_ctrl_classes=""):
        return (
            101,
            [("", item) for item in result],
            1,
            [SimplePagedResultsControl(True, size=len(result), cookie="")],
        )

    return _result


def test_whoami(mock_connection):
    r = (
        "dn: krbprincipalname=http/fasjson.example.test@example.test,"
        "cn=services,cn=accounts,dc=example,dc=test"
    )
    mock_connection.whoami_s = lambda: r

    ldap = LDAP("https://dummy.com", basedn="dc=example,dc=test")

    expected = {"dn": r[4:]}
    assert expected == ldap.whoami()


def test_get_groups(mock_connection):
    mocked = [
        {"cn": [b"admins"]},
        {"cn": [b"ipausers"]},
        {"cn": [b"editors"]},
        {"cn": [b"trust admins"]},
    ]
    mock_connection.result3 = _single_page_result_factory(mocked)

    ldap = LDAP("https://dummy.com", basedn="dc=example,dc=test")

    result = ldap.get_groups(page_number=1, page_size=0)
    expected = LDAPResult(
        items=[
            {"name": "admins"},
            {"name": "ipausers"},
            {"name": "editors"},
            {"name": "trust admins"},
        ],
        total=4,
        page_size=0,
        page_number=1,
    )
    assert result == expected


def test_get_group_members(mock_connection):
    mocked = [{"uid": [b"admin"]}]
    mock_connection.result3 = _single_page_result_factory(mocked)

    ldap = LDAP("https://dummy.com", basedn="dc=example,dc=test")

    result = ldap.get_group_members("admins", page_number=1, page_size=0)
    expected = LDAPResult(
        items=[{"username": "admin"}], total=1, page_size=0, page_number=1
    )
    assert result == expected


def test_get_user(mock_connection):
    mocked = [
        {
            "uid": [b"admin"],
            "sn": [b"Administrator"],
            "givenName": [b""],
            "mail": [b"admin@example.test"],
            "fasIRCNick": [b"admin"],
            # "fasLocale": None,
            "fasTimeZone": [b"UTC"],
            # "fasGPGKeyId": None,
            "fasCreationTime": [b"20200309103203Z"],  # %Y%m%d%H%M%SZ
            "nsAccountLock": [b"false"],
        }
    ]
    mock_connection.result3 = _single_page_result_factory(mocked)

    ldap = LDAP("https://dummy.com", basedn="dc=example,dc=test")

    expected = {
        "creation": datetime.datetime(2020, 3, 9, 10, 32, 3),
        "givenname": "",
        "ircnick": ["admin"],
        "locked": False,
        "username": "admin",
        "emails": ["admin@example.test"],
        "surname": "Administrator",
        "timezone": "UTC",
    }
    assert expected == ldap.get_user("admin")
