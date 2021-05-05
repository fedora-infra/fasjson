from functools import partial

import pytest
from fasjson.lib.ldap.client import LDAPResult
from fasjson.tests.unit.utils import get_user_api_output, get_user_ldap_data


@pytest.fixture
def mock_ldap_client(mock_ipa_client):
    yield partial(mock_ipa_client, "fasjson.web.resources.users", "ldap")


def test_user_success(client, gss_user, mock_ldap_client):
    data = get_user_ldap_data("dummy")
    mock_ldap_client(get_user=lambda u, attrs: data)

    rv = client.get("/v1/users/dummy/")

    expected = get_user_api_output("dummy")
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_user_error(client, gss_user, mock_ldap_client):
    mock_ldap_client(get_user=lambda u, attrs: None)

    rv = client.get("/v1/users/admin/")
    res = rv.get_json()

    assert 404 == rv.status_code
    assert res == {
        "name": "admin",
        "message": "User not found",
    }


def test_user_private(client, gss_user, mock_ldap_client):
    data = get_user_ldap_data("dummy")
    data["is_private"] = True
    mock_ldap_client(get_user=lambda u, attrs: data)

    rv = client.get("/v1/users/dummy/")

    assert 200 == rv.status_code
    result = rv.get_json()["result"]
    assert result["human_name"] is None
    assert result["surname"] is None
    assert result["givenname"] is None
    assert result["ircnicks"] is None
    assert result["gpgkeyids"] is None
    assert result["locale"] is None
    assert result["timezone"] is None


def test_user_private_self(client, gss_user, mock_ldap_client):
    data = get_user_ldap_data("admin")
    data["is_private"] = True
    mock_ldap_client(get_user=lambda u, attrs: data)

    rv = client.get("/v1/users/admin/")

    expected = get_user_api_output("admin")
    expected["is_private"] = True
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_user_no_private_info(client, gss_user, mock_ldap_client):
    data = get_user_ldap_data("dummy")
    del data["is_private"]
    mock_ldap_client(get_user=lambda u, attrs: data)

    rv = client.get("/v1/users/dummy/")

    expected = get_user_api_output("dummy")
    expected["is_private"] = None
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_user_with_mask(client, gss_user, mock_ldap_client):
    data = get_user_ldap_data("dummy")
    mock_ldap_client(get_user=lambda u, attrs: data)

    rv = client.get(
        "/v1/users/dummy/", headers={"X-Fields": "{username,human_name}"}
    )

    expected = {
        key: value
        for key, value in get_user_api_output("dummy").items()
        if key in ["username", "human_name"]
    }
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_users_success(client, gss_user, mock_ldap_client):
    data = [get_user_ldap_data(f"dummy-{idx}") for idx in range(1, 10)]
    result = LDAPResult(items=data)
    mock_ldap_client(get_users=lambda attrs, page_size, page_number: result,)

    rv = client.get("/v1/users/")

    expected = [get_user_api_output(f"dummy-{idx}") for idx in range(1, 10)]
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_users_with_mask(client, gss_user, mock_ldap_client):
    data = [get_user_ldap_data(f"dummy-{idx}") for idx in range(1, 10)]
    result = LDAPResult(items=data)
    mock_ldap_client(get_users=lambda attrs, page_size, page_number: result)

    rv = client.get(
        "/v1/users/", headers={"X-Fields": "{username,human_name}"}
    )

    expected = [
        {
            key: value
            for key, value in get_user_api_output(f"dummy-{idx}").items()
            if key in ["username", "human_name"]
        }
        for idx in range(1, 10)
    ]
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_user_groups_success(client, gss_user, mock_ldap_client):
    groups = ["group1", "group2"]
    result = LDAPResult(items=[{"groupname": name} for name in groups])
    mock_ldap_client(
        get_user_groups=lambda username, attrs, page_size, page_number: result,
        get_user=lambda n, attrs=None: {"cn": n},
    )

    rv = client.get("/v1/users/dummy/groups/")
    assert 200 == rv.status_code
    assert rv.get_json() == {
        "result": [
            {"groupname": name, "uri": f"http://localhost/v1/groups/{name}/"}
            for name in groups
        ]
    }


def test_user_groups_with_mask(client, gss_user, mock_ldap_client):
    groups = ["group1", "group2"]
    result = LDAPResult(
        items=[
            {
                "groupname": name,
                "irc": [f"#{name}"],
                "description": f"the {name} group",
            }
            for name in groups
        ]
    )
    mock_ldap_client(
        get_user_groups=lambda username, attrs, page_size, page_number: result,
        get_user=lambda n, attrs=None: {"cn": n},
    )

    rv = client.get(
        "/v1/users/dummy/groups/", headers={"X-Fields": "{groupname,irc}"},
    )
    assert 200 == rv.status_code
    assert rv.get_json() == {
        "result": [
            {"groupname": name, "irc": [f"#{name}"]} for name in groups
        ]
    }


def test_user_groups_error(client, gss_user, mock_ldap_client):
    mock_ldap_client(get_user=lambda n, attrs=None: None)

    rv = client.get("/v1/users/dummy/groups/")

    expected = {"name": "dummy", "message": "User does not exist"}

    assert 404 == rv.status_code
    assert rv.get_json() == expected


def test_user_agreements_success(client, gss_user, mock_ldap_client):
    agreements = ["agmt1", "agmt2"]
    result = LDAPResult(items=[{"name": name} for name in agreements])
    mock_ldap_client(
        get_user_agreements=lambda username, page_size, page_number: result,
        get_user=lambda n, attrs=None: {"cn": n},
    )

    rv = client.get("/v1/users/dummy/agreements/")
    assert 200 == rv.status_code
    assert rv.get_json() == {
        "result": [{"name": name} for name in agreements]
    }


def test_user_agreements_error(client, gss_user, mock_ldap_client):
    mock_ldap_client(get_user=lambda n, attrs=None: None)

    rv = client.get("/v1/users/dummy/agreements/")

    expected = {"name": "dummy", "message": "User does not exist"}

    assert 404 == rv.status_code
    assert rv.get_json() == expected
