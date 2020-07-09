from functools import partial

import pytest

from fasjson.lib.ldap.client import LDAPResult
from fasjson.tests.unit.utils import get_user_ldap_data, get_user_api_output


@pytest.fixture
def mock_ldap_client(mock_ipa_client):
    yield partial(mock_ipa_client, "fasjson.web.resources.users", "ldap")


def test_user_success(client, gss_user, mock_ldap_client):
    data = get_user_ldap_data("dummy")
    mock_ldap_client(get_user=lambda u: data)

    rv = client.get("/v1/users/dummy/")

    expected = get_user_api_output("dummy")
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_user_error(client, gss_user, mock_ldap_client):
    mock_ldap_client(get_user=lambda u: None)

    rv = client.get("/v1/users/admin/")
    res = rv.get_json()

    assert 404 == rv.status_code
    assert res == {
        "name": "admin",
        "message": "User not found",
    }


def test_users_success(client, gss_user, mock_ldap_client):
    data = [get_user_ldap_data(f"dummy-{idx}") for idx in range(1, 10)]
    result = LDAPResult(items=data)
    mock_ldap_client(get_users=lambda page_size, page_number: result,)

    rv = client.get("/v1/users/")

    expected = [get_user_api_output(f"dummy-{idx}") for idx in range(1, 10)]
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_user_groups_success(client, gss_user, mock_ldap_client):
    groups = ["group1", "group2"]
    result = LDAPResult(items=[{"groupname": name} for name in groups])
    mock_ldap_client(
        get_user_groups=lambda username, page_size, page_number: result,
        get_user=lambda n: {"cn": n},
    )

    rv = client.get("/v1/users/dummy/groups/")
    assert 200 == rv.status_code
    assert rv.get_json() == {
        "result": [
            {"groupname": name, "uri": f"http://localhost/v1/groups/{name}/"}
            for name in groups
        ]
    }


def test_user_groups_error(client, gss_user, mock_ldap_client):
    mock_ldap_client(get_user=lambda n: None)

    rv = client.get("/v1/users/dummy/groups/")

    expected = {"name": "dummy", "message": "User does not exist"}

    assert 404 == rv.status_code
    assert rv.get_json() == expected
