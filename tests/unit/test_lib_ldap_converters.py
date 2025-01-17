import pytest

from fasjson.lib.ldap import converters


def test_bool_true():
    c = converters.BoolConverter("locked")
    assert c.from_ldap([b"true"]) is True


def test_bool_wrong_value():
    c = converters.BoolConverter("locked")
    with pytest.raises(ValueError):
        assert c.from_ldap([b"maybe"])


def test_binary():
    c = converters.BinaryConverter("userCertificate")
    assert c.ldap_name == "userCertificate;binary"
    assert c.from_ldap([b"dummy"]) == "ZHVtbXk="
