import pytest

from fasjson.lib.ldap import converters


def test_bool_true():
    c = converters.BoolConverter("locked")
    assert c.from_ldap([b"true"]) is True


def test_bool_wrong_value():
    c = converters.BoolConverter("locked")
    with pytest.raises(ValueError):
        assert c.from_ldap([b"maybe"])
