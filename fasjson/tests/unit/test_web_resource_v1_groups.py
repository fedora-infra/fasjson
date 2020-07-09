from functools import partial

import pytest

from fasjson.lib.ldap.client import LDAPResult


@pytest.fixture
def mock_ldap_client(mock_ipa_client):
    yield partial(mock_ipa_client, "fasjson.web.resources.groups", "ldap")


def test_groups_success(client, gss_user, mock_ldap_client):
    groups = ["group1", "group2"]
    result = LDAPResult(items=[{"groupname": name} for name in groups])
    mock_ldap_client(get_groups=lambda page_size, page_number: result,)

    rv = client.get("/v1/groups/")
    assert 200 == rv.status_code
    assert rv.get_json() == {
        "result": [
            {"groupname": name, "uri": f"http://localhost/v1/groups/{name}/"}
            for name in groups
        ]
    }


def test_groups_paginate(client, gss_user, mock_ldap_client):
    result = LDAPResult(
        items=[{"groupname": "group1"}], total=2, page_number=1, page_size=1
    )
    mock_ldap_client(get_groups=lambda page_size, page_number: result,)

    rv = client.get("/v1/groups/?page_size=1")
    assert 200 == rv.status_code
    assert rv.get_json() == {
        "result": [
            {
                "groupname": "group1",
                "uri": "http://localhost/v1/groups/group1/",
            }
        ],
        "page": {
            "total_results": 2,
            "page_size": 1,
            "page_number": 1,
            "total_pages": 2,
            "next_page": "http://localhost/v1/groups/?page_size=1&page_number=2",
        },
    }


def test_groups_paginate_last_page(client, gss_user, mock_ldap_client):
    result = LDAPResult(
        items=[{"groupname": "group2"}], total=2, page_number=2, page_size=1
    )
    mock_ldap_client(get_groups=lambda page_size, page_number: result,)

    rv = client.get("/v1/groups/?page_size=1&page_number=2")
    assert 200 == rv.status_code
    assert rv.get_json()["page"] == {
        "total_results": 2,
        "page_size": 1,
        "page_number": 2,
        "total_pages": 2,
    }


def test_groups_no_groups(client, gss_user, mock_ldap_client):
    result = LDAPResult(items=[])
    mock_ldap_client(get_groups=lambda page_size, page_number: result,)
    rv = client.get("/v1/groups/")

    assert 200 == rv.status_code
    assert rv.get_json() == {"result": []}


def test_groups_error(client, gss_user):
    del client.gss_env["KRB5CCNAME"]
    rv = client.get("/v1/groups/")

    assert 401 == rv.status_code


def test_group_members_success(client, gss_user, mock_ldap_client):
    data = [{"username": "admin"}]
    result = LDAPResult(items=data)
    mock_ldap_client(
        get_group_members=lambda name, page_size, page_number: result,
        get_group=lambda n: {"cn": n},
    )
    rv = client.get("/v1/groups/admins/members/")

    expected = {
        "result": [
            {"username": "admin", "uri": "http://localhost/v1/users/admin/"}
        ]
    }
    assert 200 == rv.status_code
    assert expected == rv.get_json()


def test_group_members_error(client, gss_user, mock_ldap_client):
    mock_ldap_client(
        # get_group_members=lambda name, ps, pn: result,
        get_group=lambda n: None,
    )

    rv = client.get("/v1/groups/editors/members/")

    expected = {
        "groupname": "editors",
        "message": "Group not found",
    }
    assert 404 == rv.status_code
    assert expected == rv.get_json()


def test_group_sponsors_success(client, gss_user, mock_ldap_client):
    result = [{"username": "admin"}]
    mock_ldap_client(
        get_group_sponsors=lambda groupname: result,
        get_group=lambda n: {"cn": n},
    )
    rv = client.get("/v1/groups/admins/sponsors/")

    expected = {
        "result": [
            {"username": "admin", "uri": "http://localhost/v1/users/admin/"}
        ]
    }
    assert 200 == rv.status_code
    assert expected == rv.get_json()


def test_group_sponsors_error(client, gss_user, mock_ldap_client):
    mock_ldap_client(get_group=lambda n: None,)

    rv = client.get("/v1/groups/editors/sponsors/")

    expected = {
        "groupname": "editors",
        "message": "Group not found",
    }
    assert 404 == rv.status_code
    assert expected == rv.get_json()


def test_group_success(client, gss_user, mock_ldap_client):
    mock_ldap_client(get_group=lambda n: {"groupname": "dummy-group"},)

    rv = client.get("/v1/groups/dummy-group/")

    expected = {
        "groupname": "dummy-group",
        "uri": "http://localhost/v1/groups/dummy-group/",
    }
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_group_not_found(client, gss_user, mock_ldap_client):
    mock_ldap_client(get_group=lambda n: None)
    rv = client.get("/v1/groups/dummy-group/")
    assert rv.status_code == 404
