import json
from datetime import datetime, timezone

from fasjson.lib.ldap.client import LDAPResult


def _get_user_ldap_data(name):
    return {
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
    data["ircnick"] = data["locale"] = data["timezone"] = None
    data["uri"] = f"http://localhost/v1/users/{name}/"
    return data


def test_user_success(client, gss_user, mock_ldap_client):
    data = _get_user_ldap_data("dummy")
    mock_ldap_client("fasjson.web.resources.users", get_user=lambda u: data)

    rv = client.get("/v1/users/dummy/")

    expected = _get_user_api_output("dummy")
    assert 200 == rv.status_code
    assert json.loads(rv.data) == {"result": expected}


def test_user_error(client, gss_user, mock_ldap_client):
    mock_ldap_client("fasjson.web.resources.users", get_user=lambda u: None)

    rv = client.get("/v1/users/admin/")
    res = json.loads(rv.data)

    assert 404 == rv.status_code
    assert res == {
        "name": "admin",
        "message": "User not found",
    }


def test_users_success(client, gss_user, mock_ldap_client):
    groups = ["group1", "group2"]
    result = LDAPResult(items=[{"name": name} for name in groups])
    mock_ldap_client(
        "fasjson.web.resources.groups",
        get_groups=lambda page_size, page_number: result,
    )

    rv = client.get("/v1/groups/")
    assert 200 == rv.status_code
    assert json.loads(rv.data) == {
        "result": [
            {"name": name, "uri": f"http://localhost/v1/groups/{name}/"}
            for name in groups
        ]
    }

    data = [_get_user_ldap_data(f"dummy-{idx}") for idx in range(1, 10)]
    result = LDAPResult(items=data)
    mock_ldap_client(
        "fasjson.web.resources.users",
        get_users=lambda page_size, page_number: result,
    )

    rv = client.get("/v1/users/")

    expected = [_get_user_api_output(f"dummy-{idx}") for idx in range(1, 10)]
    assert 200 == rv.status_code
    assert json.loads(rv.data) == {"result": expected}
