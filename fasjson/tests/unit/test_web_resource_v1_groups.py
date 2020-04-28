import json

from fasjson.lib.ldap.client import LDAPResult


def test_groups_success(client, gss_user, mock_ldap_client):
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


def test_groups_success_paginate(client, gss_user, mock_ldap_client):
    result = LDAPResult(
        items=[{"name": "group1"}], total=2, page_number=1, page_size=1
    )
    mock_ldap_client(
        "fasjson.web.resources.groups",
        get_groups=lambda page_size, page_number: result,
    )

    rv = client.get("/v1/groups/?page_size=1")
    assert 200 == rv.status_code
    assert json.loads(rv.data) == {
        "result": [
            {"name": "group1", "uri": "http://localhost/v1/groups/group1/"}
        ],
        "page": {
            "total_results": 2,
            "page_size": 1,
            "page_number": 1,
            "total_pages": 2,
            "next_page": "http://localhost/v1/groups/?page_size=1&page=2",
        },
    }


def test_groups_no_groups(client, gss_user, mock_ldap_client):
    result = LDAPResult(items=[])
    mock_ldap_client(
        "fasjson.web.resources.groups",
        get_groups=lambda page_size, page_number: result,
    )
    rv = client.get("/v1/groups/")

    assert 200 == rv.status_code
    assert json.loads(rv.data) == {"result": []}


def test_groups_error(client, gss_user):
    del client.gss_env["KRB5CCNAME"]
    rv = client.get("/v1/groups/")

    assert 401 == rv.status_code


def test_group_members_success(client, gss_user, mock_ldap_client):
    data = [{"username": "admin"}]
    result = LDAPResult(items=data)
    mock_ldap_client(
        "fasjson.web.resources.groups",
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
    assert expected == json.loads(rv.data)


def test_group_members_error(client, gss_user, mock_ldap_client):
    mock_ldap_client(
        "fasjson.web.resources.groups",
        # get_group_members=lambda name, ps, pn: result,
        get_group=lambda n: None,
    )

    rv = client.get("/v1/groups/editors/members/")

    expected = {
        "name": "editors",
        "message": (
            "Group not found. You have requested this URI [/v1/groups/editors/members/] "
            "but did you mean /v1/groups/<name:name>/members/ or /v1/groups/<name:name>/ ?"
        ),
    }
    assert 404 == rv.status_code
    assert expected == json.loads(rv.data)


def test_group_success(client, gss_user, mock_ldap_client):
    mock_ldap_client(
        "fasjson.web.resources.groups",
        get_group=lambda n: {"name": "dummy-group"},
    )

    rv = client.get("/v1/groups/dummy-group/")

    expected = {
        "name": "dummy-group",
        "uri": "http://localhost/v1/groups/dummy-group/",
    }
    assert 200 == rv.status_code
    assert json.loads(rv.data) == {"result": expected}


def test_group_not_found(client, gss_user, mock_ldap_client):
    mock_ldap_client("fasjson.web.resources.groups", get_group=lambda n: None)
    rv = client.get("/v1/groups/dummy-group/")
    assert rv.status_code == 404
