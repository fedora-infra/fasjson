import types
import datetime

from ldap.controls.pagedresults import SimplePagedResultsControl

from fasjson.lib import ldaputils


def test_whoami(mocker):
    r = (
        "dn: krbprincipalname=http/fasjson.example.test@example.test,"
        "cn=services,cn=accounts,dc=example,dc=test"
    )
    L = mocker.patch("ldap.initialize")
    L.return_value = types.SimpleNamespace(
        protocol_version=3,
        set_option=lambda a, b: a,
        sasl_interactive_bind_s=lambda s, n: "",
        whoami_s=lambda: r,
    )
    ldap = ldaputils.LDAP("https://dummy.com")

    expected = {
        "krbprincipalname": "http/fasjson.example.test@example.test",
        "cn": ["services", "accounts"],
        "dc": ["example", "test"],
    }

    assert (r, expected) == ldap.whoami()


def test_get_groups(mocker):
    mocked = [
        ("", {"cn": [b"admins"]}),
        ("", {"cn": [b"ipausers"]}),
        ("", {"cn": [b"editors"]}),
        ("", {"cn": [b"trust admins"]}),
    ]

    def search_ext(a, b, c, attrlist="", serverctrls=""):
        return mocked

    def result3(msgid, resp_ctrl_classes=""):
        return (
            101,
            mocked,
            2,
            [SimplePagedResultsControl(True, size=20, cookie="")],
        )

    L = mocker.patch("ldap.initialize")
    L.return_value = types.SimpleNamespace(
        protocol_version=3,
        set_option=lambda a, b: a,
        sasl_interactive_bind_s=lambda s, n: "",
        result3=result3,
        search_ext=search_ext,
    )
    ldap = ldaputils.LDAP("https://dummy.com")

    assert ldap.get_groups() == (
        2,
        0,
        None,
        ["admins", "ipausers", "editors", "trust admins"],
    )


def test_get_group_members(mocker):
    mocked = [("", {"uid": [b"admin"]})]

    def search_ext(a, b, c, attrlist="", serverctrls=""):
        return mocked

    def result3(msgid, resp_ctrl_classes=""):
        return (
            101,
            mocked,
            1,
            [SimplePagedResultsControl(True, size=20, cookie="")],
        )

    L = mocker.patch("ldap.initialize")
    L.return_value = types.SimpleNamespace(
        protocol_version=3,
        set_option=lambda a, b: a,
        sasl_interactive_bind_s=lambda s, n: "",
        result3=result3,
        search_ext=search_ext,
    )
    ldap = ldaputils.LDAP("https://dummy.com")

    assert ldap.get_group_members("admins") == (1, 0, None, ["admin"])


def test_get_user(mocker):
    mocked = {
        "uid": [b"admin"],
        "sn": [b"Administrator"],
        "givenName": [b""],
        "mail": [b"admin@example.test"],
        "fasIRCNick": [b""],
        "fasLocale": [b""],
        "fasTimeZone": [b""],
        "fasGPGKeyId": None,
        "fasCreationTime": [b"20200309103203Z"],  # %Y%m%d%H%M%SZ
        "nsAccountLock": [b"false"],
    }

    def search_s(a, b, c, attrlist="", serverctrls=""):
        return [("", mocked)]

    L = mocker.patch("ldap.initialize")
    L.return_value = types.SimpleNamespace(
        protocol_version=3,
        set_option=lambda a, b: a,
        sasl_interactive_bind_s=lambda s, n: "",
        search_s=search_s,
    )
    ldap = ldaputils.LDAP("https://dummy.com")

    expected = {
        "creationts": datetime.datetime(2020, 3, 9, 10, 32, 3),
        "givenname": "",
        "gpgkeyids": None,
        "ircnick": "",
        "locale": "",
        "locked": False,
        "login": "admin",
        "mails": ["admin@example.test"],
        "surename": "Administrator",
        "timezone": "",
    }

    assert expected == ldap.get_user("admin")
