from functools import partial

import pytest

from fasjson.lib.ldap.client import LDAPResult
from fasjson.tests.unit.utils import get_user_ldap_data, get_user_api_output


@pytest.fixture
def mock_ldap_client(mock_ipa_client):
    yield partial(mock_ipa_client, "fasjson.web.resources.search", "ldap")


@pytest.fixture()
def ldap_with_search_result(mock_ldap_client, gss_user):
    def mock(num, page_size, page_number, total_results):
        data = [
            get_user_ldap_data(f"dummy-{idx + 1}") for idx in range(0, num)
        ]
        result = LDAPResult(
            items=data,
            total=total_results,
            page_size=page_size,
            page_number=page_number,
        )
        return mock_ldap_client(search_users=lambda *a, **kw: result)

    return mock


def test_search_user_success(client, ldap_with_search_result):
    ldap_with_search_result(
        num=9, page_size=40, page_number=1, total_results=9
    )
    rv = client.get("/v1/search/users/?username=dummy")

    expected = [get_user_api_output(f"dummy-{idx}") for idx in range(1, 10)]
    page = {
        "total_results": 9,
        "page_size": 40,
        "page_number": 1,
        "total_pages": 1,
    }
    assert 200 == rv.status_code
    print(expected[0])
    print(rv.get_json()["result"][0])
    assert rv.get_json() == {"result": expected, "page": page}


def test_search_user_not_found(client, ldap_with_search_result):
    ldap_with_search_result(
        num=0, page_size=40, page_number=1, total_results=0
    )
    rv = client.get("/v1/search/users/?username=somethingobscure")
    expected = {
        "result": [],
        "page": {
            "total_results": 0,
            "page_size": 40,
            "page_number": 1,
            "total_pages": 0,
        },
    }
    assert 200 == rv.status_code
    assert rv.get_json() == expected


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


def test_search_user_page_size_none(client, ldap_with_search_result):
    ldap_with_search_result(
        num=0, page_size=40, page_number=1, total_results=0
    )
    rv = client.get("/v1/search/users/?username=somethinginsignificant")

    expected = {
        "result": [],
        "page": {
            "total_results": 0,
            "page_size": 40,
            "page_number": 1,
            "total_pages": 0,
        },
    }
    assert 200 == rv.status_code
    assert expected == rv.get_json()


def test_search_user_outside_page_range(client, ldap_with_search_result):
    ldap_with_search_result(
        num=0, page_size=2, page_number=6, total_results=9
    )
    rv = client.get(
        "/v1/search/users/?username=dummy&page_number=6&page_size=2"
    )

    expected = {
        "result": [],
        "page": {
            "total_results": 9,
            "page_size": 2,
            "page_number": 6,
            "total_pages": 5,
        },
    }
    assert 200 == rv.status_code
    assert expected == rv.get_json()
