import types
import datetime
from unittest import mock

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


def test_whoami_user(mock_connection):
    r = "dn: uid=dummy,cn=users,cn=accounts,dc=example,dc=test"
    mock_connection.whoami_s = lambda: r

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")

    expected = {"dn": r[4:], "username": "dummy"}
    assert expected == ldap.whoami()


def test_whoami_service(mock_connection):
    r = (
        "dn: krbprincipalname=test/fasjson.example.test@example.test,"
        "cn=services,cn=accounts,dc=example,dc=test"
    )
    mock_connection.whoami_s = lambda: r

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")

    expected = {"dn": r[4:], "service": "test/fasjson.example.test"}
    assert expected == ldap.whoami()


def test_get_groups(mock_connection):
    mocked = [
        {"cn": [b"admins"]},
        {"cn": [b"ipausers"]},
        {"cn": [b"editors"]},
        {"cn": [b"trust admins"]},
    ]
    mock_connection.result3 = _single_page_result_factory(mocked)

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")

    result = ldap.get_groups(page_number=1, page_size=0)
    expected = LDAPResult(
        items=[
            {"groupname": "admins"},
            {"groupname": "ipausers"},
            {"groupname": "editors"},
            {"groupname": "trust admins"},
        ],
        total=4,
        page_size=0,
        page_number=1,
    )
    assert result == expected


def test_get_group(mock_connection):
    mocked = [{"cn": [b"dummy-group"]}]
    mock_connection.result3 = _single_page_result_factory(mocked)

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")

    assert ldap.get_group("dummy-group") == {"groupname": "dummy-group"}


def test_get_group_not_found(mock_connection):
    mock_connection.result3 = _single_page_result_factory([])
    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")
    assert ldap.get_group("dummy-group") is None


def test_get_group_members(mock_connection):
    mocked = [{"uid": [b"admin"]}]
    mock_connection.result3 = _single_page_result_factory(mocked)

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")

    result = ldap.get_group_members("admins", page_number=1, page_size=0)
    expected = LDAPResult(
        items=[{"username": "admin"}], total=1, page_size=0, page_number=1
    )
    assert result == expected


def test_get_group_sponsors(mock_connection):
    mocked = [
        {
            "memberManager": [
                b"uid=admin,cn=users,cn=accounts,dc=example,dc=test"
            ]
        }
    ]
    mocked_conversion = [{"username": "admin"}]
    mock_connection.result3 = _single_page_result_factory(mocked)

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")
    with mock.patch.object(
        ldap, "_sponsors_to_users", side_effect=[mocked_conversion]
    ):
        result = ldap.get_group_sponsors(groupname="admins")

    expected = [{"username": "admin"}]
    assert result == expected


def test_get_group_sponsors_none(mock_connection):
    mock_connection.result3 = _single_page_result_factory([])
    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")
    assert ldap.get_group_sponsors("dummy") == []


def test_sponsors_to_users(mock_connection):
    mocked = [{"uid": [b"admin"]}]
    mock_connection.result3 = _single_page_result_factory(mocked)

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")

    sponsors_dn = LDAPResult(
        items=[
            {
                "sponsors": [
                    "uid=admin,cn=users,cn=accounts,dc=example,dc=test"
                ]
            }
        ]
    )

    result = ldap._sponsors_to_users(sponsors_dn)
    expected = [{"username": "admin"}]
    assert result == expected


def test_get_users(mock_connection):
    def _get_mock_result(idx):
        return {
            "uid": [f"dummy-{idx}".encode("ascii")],
            "sn": [b""],
            "givenName": [b""],
            "mail": [f"dummy-{idx}@example.test".encode("ascii")],
            "fasCreationTime": [b"20200309103203Z"],
            "nsAccountLock": [b"false"],
        }

    mocked = [_get_mock_result(i) for i in range(1, 4)]
    mock_connection.result3 = _single_page_result_factory(mocked)

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")

    result = ldap.get_users(page_number=1, page_size=0)
    creation_dt = datetime.datetime(2020, 3, 9, 10, 32, 3)

    def _get_expected(idx):
        return {
            "creation": creation_dt,
            "givenname": "",
            "locked": False,
            "username": f"dummy-{idx}",
            "emails": [f"dummy-{idx}@example.test"],
            "surname": "",
        }

    expected = LDAPResult(
        items=[_get_expected(i) for i in range(1, 4)],
        total=3,
        page_size=0,
        page_number=1,
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

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")

    expected = {
        "creation": datetime.datetime(2020, 3, 9, 10, 32, 3),
        "givenname": "",
        "ircnicks": ["admin"],
        "locked": False,
        "username": "admin",
        "emails": ["admin@example.test"],
        "surname": "Administrator",
        "timezone": "UTC",
    }
    assert expected == ldap.get_user("admin")


def test_get_user_not_found(mock_connection):
    mock_connection.result3 = _single_page_result_factory([])
    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")
    assert ldap.get_user("dummy") is None


def test_get_user_groups(mock_connection):
    mocked = [
        {"cn": [b"admins"]},
        {"cn": [b"ipausers"]},
        {"cn": [b"editors"]},
        {"cn": [b"trust admins"]},
    ]
    mock_connection.result3 = _single_page_result_factory(mocked)

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")

    result = ldap.get_user_groups(
        username="dummy", page_number=1, page_size=0
    )
    expected = LDAPResult(
        items=[
            {"groupname": "admins"},
            {"groupname": "ipausers"},
            {"groupname": "editors"},
            {"groupname": "trust admins"},
        ],
        total=4,
        page_size=0,
        page_number=1,
    )
    assert result == expected


def test_search_users(mock_connection):
    def _get_mock_result(idx):
        return {
            "uid": [f"dummy-{idx}".encode("ascii")],
            "sn": [b""],
            "givenName": [b""],
            "mail": [f"dummy-{idx}@example.test".encode("ascii")],
            "fasCreationTime": [b"20200309103203Z"],
            "nsAccountLock": [b"false"],
        }

    mocked = [_get_mock_result(i) for i in range(1, 4)]
    mock_connection.result3 = _single_page_result_factory(mocked)

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")

    result = ldap.search_users(
        username="dummy",
        email="dummy",
        ircnick="dummy-1@example.test",
        givenname="",
        surname="",
        page_number=1,
        page_size=0,
    )
    creation_dt = datetime.datetime(2020, 3, 9, 10, 32, 3)

    def _get_expected(idx):
        return {
            "creation": creation_dt,
            "givenname": "",
            "locked": False,
            "username": f"dummy-{idx}",
            "emails": [f"dummy-{idx}@example.test"],
            "surname": "",
        }

    expected = LDAPResult(
        items=[_get_expected(i) for i in range(1, 4)],
        total=3,
        page_size=0,
        page_number=1,
    )
    assert result == expected


def test_get_paged_search_filters(mock_connection):
    mocked = []

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")
    with mock.patch.object(
        ldap, "_do_search", side_effect=[mocked]
    ) as do_search:
        result = ldap.search_users(
            page_number=2,
            page_size=3,
            username="something",
            email=None,
            ircnick=None,
            givenname=None,
            surname=None,
        )

    called_filters = [call[1]["filters"] for call in do_search.call_args_list]
    assert called_filters == [
        "(&(&(objectClass=fasUser)(!(nsAccountLock=TRUE)))(&(uid=*something*)))"
    ]
    expected = LDAPResult(items=[], total=0, page_size=3, page_number=2,)
    assert result == expected


def test_get_paged_groups(mock_connection):
    mocked = [
        {"cn": [f"group-{idx}".encode("ascii")]} for idx in range(1, 12)
    ]

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")
    with mock.patch.object(
        ldap, "_do_search", side_effect=[mocked, mocked[3:6]]
    ) as do_search:
        result = ldap.get_groups(page_number=2, page_size=3)

    called_filters = [call[1]["filters"] for call in do_search.call_args_list]
    assert called_filters == [
        "(objectClass=fasGroup)",
        "(&(objectClass=fasGroup)(|(cn=group-4)(cn=group-5)(cn=group-6)))",
    ]
    expected = LDAPResult(
        items=[
            {"groupname": "group-4"},
            {"groupname": "group-5"},
            {"groupname": "group-6"},
        ],
        total=11,
        page_size=3,
        page_number=2,
    )
    assert result == expected


def test_get_paged_search_no_results(mock_connection):
    mocked = []

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")
    with mock.patch.object(
        ldap, "_do_search", side_effect=[mocked]
    ) as do_search:
        result = ldap.search_users(
            page_number=2,
            page_size=3,
            username="something",
            email="something@example.test",
            ircnick="something",
            givenname="some",
            surname="thing",
        )

    called_filters = [call[1]["filters"] for call in do_search.call_args_list]
    assert called_filters == [
        (
            "(&(&(objectClass=fasUser)(!(nsAccountLock=TRUE)))(&(uid=*something*)"
            "(mail=something@example.test)(fasIRCNick=*something*)"
            "(givenName=*some*)(sn=*thing*)))"
        )
    ]
    expected = LDAPResult(items=[], total=0, page_size=3, page_number=2,)
    assert result == expected


def test_do_search_paged(mock_connection):
    dummy_server_control = object()
    pages = [
        (
            101,
            [("", {"cn": [b"group-1"]})],
            1,
            [
                dummy_server_control,
                SimplePagedResultsControl(True, size=2, cookie="ignore"),
            ],
        ),
        (
            101,
            [("", {"cn": [b"group-2"]})],
            1,
            [
                dummy_server_control,
                SimplePagedResultsControl(True, size=2, cookie=""),
            ],
        ),
    ]
    mock_connection.result3 = mock.Mock(side_effect=pages)

    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")
    result = ldap.get_groups(0, 1)

    expected = LDAPResult(
        items=[{"groupname": "group-1"}, {"groupname": "group-2"}],
        total=2,
        page_size=0,
        page_number=1,
    )
    assert result == expected


def test_do_search_other_server_control(mock_connection):
    dummy_server_control = object()
    ldap_return = [101, [], 1, [dummy_server_control]]
    mock_connection.result3 = mock.Mock(return_value=ldap_return)
    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")
    ldap.get_groups(0, 1)
    # No loop
    assert mock_connection.result3.call_count == 1


def test_do_search_no_server_control(mock_connection):
    ldap_return = [101, [], 1, []]
    mock_connection.result3 = mock.Mock(return_value=ldap_return)
    ldap = LDAP("ldap://dummy.com", basedn="dc=example,dc=test")
    ldap.get_groups(0, 1)
    # No loop
    assert mock_connection.result3.call_count == 1
