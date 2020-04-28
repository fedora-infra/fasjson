import pytest

from fasjson.lib.ldap.client import LDAPResult


@pytest.fixture
def ldap_result():
    return LDAPResult(
        items=[{"name": "dummy-1"}, {"name": "dummy-2"}],
        total=4,
        page_size=0,
        page_number=1,
    )


def test_ldap_result_repr(ldap_result):
    assert repr(ldap_result) == "<LDAPResult items=[2 items] page=1>"


def test_ldap_result_cmp(ldap_result):
    result_1 = ldap_result
    result_2 = LDAPResult(items=ldap_result.items)
    assert result_1 != result_2


def test_ldap_result_cmp_invalid(ldap_result):
    with pytest.raises(ValueError):
        ldap_result == ["a", "b", "c"]
