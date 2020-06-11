from datetime import datetime, timezone
from functools import partial

import pytest

from fasjson.lib.ldap.client import LDAPResult


@pytest.fixture
def mock_ldap_client(mock_ipa_client):
    yield partial(mock_ipa_client, "fasjson.web.resources.search", "ldap")


@pytest.fixture
def client_with_search_result(mock_ldap_client):
    data = [_get_user_ldap_data(f"dummy-{idx}") for idx in range(1, 10)]
    result = LDAPResult(items=data)
    yield mock_ldap_client(search_users=lambda *a, **kw: result)


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


def test_search_user_success(client, gss_user, client_with_search_result):
    rv = client.get("/v1/search/users/?username=dummy")

    expected = [_get_user_api_output(f"dummy-{idx}") for idx in range(1, 10)]
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_search_user_not_found(client, gss_user, mock_ldap_client):
    result = LDAPResult(items=[])
    mock_ldap_client(search_users=lambda *a, **kw: result)

    rv = client.get("/v1/search/users/?username=somethingobscure")

    assert 200 == rv.status_code
    assert rv.get_json() == {"result": []}


def test_search_user_no_args(client, gss_user, mock_ldap_client):
    mock_ldap_client(search_users=lambda *a, **kw: None)

    rv = client.get("/v1/search/users/")

    expected = {"message": "At least one search term must be provided"}
    assert 400 == rv.status_code
    assert expected == rv.get_json()


def test_search_user_short_search_term(client, gss_user, mock_ldap_client):
    mock_ldap_client(search_users=lambda *a, **kw: None)

    rv = client.get("/v1/search/users/?username=so")

    expected = {
        "message": "Search term must be at least 3 characters long.",
        "search_term": "username",
        "search_value": "so",
    }
    assert 400 == rv.status_code
    assert expected == rv.get_json()


def test_search_user_page_size(client, gss_user, mock_ldap_client):
    mock_ldap_client(search_users=lambda *a, **kw: None)

    rv = client.get(
        "/v1/search/users/?username=somethinginsignificant&page_size=123"
    )

    expected = {
        "page_size": 123,
        "message": "Page size cannot be greater than 40 when searching.",
    }
    assert 400 == rv.status_code
    assert expected == rv.get_json()
