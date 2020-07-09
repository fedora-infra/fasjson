from datetime import datetime, timezone
from functools import partial

import pytest

from fasjson.lib.ldap.client import LDAPResult


@pytest.fixture
def mock_ldap_client(mock_ipa_client):
    yield partial(mock_ipa_client, "fasjson.web.resources.users", "ldap")


def _get_user_ldap_data(name):
    return {
        "certificates": None,
        "creation": datetime(2020, 3, 9, 10, 32, 3, tzinfo=timezone.utc),
        "givenname": "",
        "gpgkeyids": None,
        "locked": False,
        "username": name,
        "emails": [f"{name}@example.test"],
        "surname": name,
    }


def _get_user_api_output(name):
    data = _get_user_ldap_data(name)
    data["creation"] = data["creation"].isoformat()
    data["ircnicks"] = data["locale"] = data["timezone"] = None
    data["uri"] = f"http://localhost/v1/users/{name}/"
    return data


def test_user_success(client, gss_user, mock_ldap_client):
    data = _get_user_ldap_data("dummy")
    mock_ldap_client(get_user=lambda u: data)

    rv = client.get("/v1/users/dummy/")

    expected = _get_user_api_output("dummy")
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
    data = [_get_user_ldap_data(f"dummy-{idx}") for idx in range(1, 10)]
    result = LDAPResult(items=data)
    mock_ldap_client(get_users=lambda page_size, page_number: result,)

    rv = client.get("/v1/users/")

    expected = [_get_user_api_output(f"dummy-{idx}") for idx in range(1, 10)]
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
