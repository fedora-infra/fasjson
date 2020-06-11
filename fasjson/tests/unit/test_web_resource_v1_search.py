from datetime import datetime, timezone
from functools import partial

import pytest

from fasjson.lib.ldap.client import LDAPResult


@pytest.fixture
def mock_ldap_client(mock_ipa_client):
    yield partial(mock_ipa_client, "fasjson.web.resources.search", "ldap")


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


def test_search_user_success_list(client, gss_user, mock_ldap_client):
    data = [_get_user_ldap_data(f"dummy-{idx}") for idx in range(1, 10)]
    result = LDAPResult(items=data)
    mock_ldap_client(search_users=lambda search_term, page_size, page_number: result,)

    rv = client.get("/v1/search/users/dummy/")

    expected = [_get_user_api_output(f"dummy-{idx}") for idx in range(1, 10)]
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_search_user_success_single(client, gss_user, mock_ldap_client):
    data = [_get_user_ldap_data(f"dummy-{idx}") for idx in range(1, 2)]
    result = LDAPResult(items=data)
    mock_ldap_client(search_users=lambda search_term, page_size, page_number: result,)

    rv = client.get("/v1/search/users/dummy-1/")

    expected = [_get_user_api_output(f"dummy-{idx}") for idx in range(1, 2)]
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_search_user_not_found(client, gss_user, mock_ldap_client):
    data = []
    result = LDAPResult(items=data)
    mock_ldap_client(search_users=lambda search_term, page_size, page_number: result,)

    rv = client.get("/v1/search/users/somethingobscure/")

    assert 200 == rv.status_code
    assert rv.get_json() == {"result": []}


def test_search_user_short_search_term(client, gss_user, mock_ldap_client):
    mock_ldap_client(search_users=lambda page_size, page_number, model, filters, sub_dn: None,)

    rv = client.get("/v1/search/users/so/")

    expected = {
        "search_term": "so",
        "message": "Search term must be at least 3 characters long.",
    }
    assert 403 == rv.status_code
    assert expected == rv.get_json()


def test_search_user_page_size(client, gss_user, mock_ldap_client):
    mock_ldap_client(search_users=lambda page_size, page_number, model, filters, sub_dn: None,)

    rv = client.get("/v1/search/users/something/?page_size=123")

    expected = {
        "page_size": 123,
        "message": "Page size cannot be greater than 40 when searching.",
    }
    assert 403 == rv.status_code
    assert expected == rv.get_json()
