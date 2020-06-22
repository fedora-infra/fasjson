from datetime import datetime, timezone
from functools import partial

import pytest

from fasjson.lib.ldap.client import LDAPResult


@pytest.fixture
def mock_ldap_client(mock_ipa_client):
    yield partial(mock_ipa_client, "fasjson.web.resources.search", "ldap")


@pytest.fixture()
def ldap_with_search_result(mock_ldap_client, gss_user):
    def mock(num_of_results):
        data = [_get_user_ldap_data(f"dummy-{idx + 1}") for idx in range(0, num_of_results)]
        result = LDAPResult(items=data)
        return mock_ldap_client(search_users=lambda *a, **kw: result)
    return mock


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


def test_search_user_success(client, ldap_with_search_result):
    ldap_with_search_result(9)
    rv = client.get("/v1/search/users/?username=dummy")

    expected = [_get_user_api_output(f"dummy-{idx}") for idx in range(1, 10)]
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_search_user_not_found(client, ldap_with_search_result):
    ldap_with_search_result(0)
    rv = client.get("/v1/search/users/?username=somethingobscure")

    assert 200 == rv.status_code
    assert rv.get_json() == {"result": []}


def test_search_user_no_args(client, gss_user, mock_ldap_client):
    mock_ldap_client(search_users=lambda *a, **kw: None)

    rv = client.get("/v1/search/users/")

    expected = {"message": "At least one search term must be provided."}
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


def test_search_user_page_size_too_big(client, gss_user, mock_ldap_client):
    mock_ldap_client(search_users=lambda *a, **kw: None)

    rv = client.get(
        "/v1/search/users/?username=somethinginsignificant&page_size=123"
    )

    expected = {
        "page_size": 123,
        "message": "Page size must be between 1 and 40 when searching.",
    }
    assert 400 == rv.status_code
    assert expected == rv.get_json()


def test_search_user_page_size_zero(client, gss_user, mock_ldap_client):
    mock_ldap_client(search_users=lambda *a, **kw: None)

    rv = client.get(
        "/v1/search/users/?username=somethinginsignificant&page_size=0"
    )

    expected = {
        "page_size": 0,
        "message": "Page size must be between 1 and 40 when searching.",
    }
    assert 400 == rv.status_code
    assert expected == rv.get_json()
