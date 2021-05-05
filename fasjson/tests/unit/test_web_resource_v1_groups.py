from functools import partial

import pytest
from fasjson.lib.ldap.client import LDAPResult


@pytest.fixture
def mock_ldap_client(mock_ipa_client):
    yield partial(mock_ipa_client, "fasjson.web.resources.groups", "ldap")


def test_groups_success(client, gss_user, mock_ldap_client):
    groups = ["group1", "group2"]
    result = LDAPResult(
        items=[
            {
                "groupname": name,
                "description": f"the {name} group",
                "mailing_list": f"{name}@groups.com",
                "url": f"www.{name}.com",
                "irc": [f"#{name}"],
            }
            for name in groups
        ]
    )
    mock_ldap_client(get_groups=lambda attrs, page_size, page_number: result)

    rv = client.get("/v1/groups/")
    assert 200 == rv.status_code
    assert rv.get_json() == {
        "result": [
            {
                "groupname": name,
                "description": f"the {name} group",
                "mailing_list": f"{name}@groups.com",
                "url": f"www.{name}.com",
                "irc": [f"#{name}"],
                "uri": f"http://localhost/v1/groups/{name}/",
            }
            for name in groups
        ]
    }


def test_groups_with_mask(client, gss_user, mock_ldap_client, mocker):
    groups = ["group1", "group2"]
    result = LDAPResult(
        items=[
            {
                "groupname": name,
                "description": f"the {name} group",
                "mailing_list": f"{name}@groups.com",
                "url": f"www.{name}.com",
                "irc": [f"#{name}"],
            }
            for name in groups
        ]
    )
    mock = mock_ldap_client(get_groups=mocker.Mock(return_value=result))

    rv = client.get(
        "/v1/groups/", headers={"X-Fields": "{groupname,description,uri}"}
    )
    assert 200 == rv.status_code
    assert rv.get_json() == {
        "result": [
            {
                "groupname": name,
                "description": f"the {name} group",
                "uri": f"http://localhost/v1/groups/{name}/",
            }
            for name in groups
        ]
    }
    mock.get_groups.assert_called_with(
        attrs=["groupname", "description", "uri"],
        page_size=None,
        page_number=1,
    )


def test_groups_no_groups(client, gss_user, mock_ldap_client):
    result = LDAPResult(items=[])
    mock_ldap_client(get_groups=lambda attrs, page_size, page_number: result)
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
        get_group_members=lambda name, attrs, page_size, page_number: result,
        get_group=lambda n, attrs=None: {"cn": n},
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
        get_group=lambda n, attrs=None: None,
    )

    rv = client.get("/v1/groups/editors/members/")

    expected = {
        "groupname": "editors",
        "message": "Group not found",
    }
    assert 404 == rv.status_code
    assert expected == rv.get_json()


def test_group_members_with_mask(client, gss_user, mock_ldap_client):
    data = [
        {
            "username": "admin",
            "emails": ["admin@example.test"],
            "timezone": "UTC",
        }
    ]
    result = LDAPResult(items=data)
    mock_ldap_client(
        get_group_members=lambda name, attrs, page_size, page_number: result,
        get_group=lambda n, attrs=None: {"cn": n},
    )
    rv = client.get(
        "/v1/groups/admins/members/",
        headers={"X-Fields": "{username,emails,uri}"},
    )

    expected = {
        "result": [
            {
                "username": "admin",
                "emails": ["admin@example.test"],
                "uri": "http://localhost/v1/users/admin/",
            }
        ]
    }
    assert 200 == rv.status_code
    assert expected == rv.get_json()


def test_group_sponsors_success(client, gss_user, mock_ldap_client):
    result = [{"username": "admin"}]
    mock_ldap_client(
        get_group_sponsors=lambda groupname, attrs: result,
        get_group=lambda n, attrs=None: {"cn": n},
    )
    rv = client.get("/v1/groups/admins/sponsors/")

    expected = {
        "result": [
            {"username": "admin", "uri": "http://localhost/v1/users/admin/"}
        ]
    }
    assert 200 == rv.status_code
    assert expected == rv.get_json()


def test_group_sponsors_with_mask(client, gss_user, mock_ldap_client):
    result = [
        {
            "username": "admin",
            "emails": ["admin@example.test"],
            "timezone": "UTC",
        }
    ]
    mock_ldap_client(
        get_group_sponsors=lambda groupname, attrs: result,
        get_group=lambda n, attrs=None: {"cn": n},
    )
    rv = client.get(
        "/v1/groups/admins/sponsors/",
        headers={"X-Fields": "{username,emails,uri}"},
    )

    expected = {
        "result": [
            {
                "username": "admin",
                "emails": ["admin@example.test"],
                "uri": "http://localhost/v1/users/admin/",
            }
        ]
    }
    assert 200 == rv.status_code
    assert expected == rv.get_json()


def test_group_sponsors_error(client, gss_user, mock_ldap_client):
    mock_ldap_client(get_group=lambda n, attrs=None: None,)

    rv = client.get("/v1/groups/editors/sponsors/")

    expected = {
        "groupname": "editors",
        "message": "Group not found",
    }
    assert 404 == rv.status_code
    assert expected == rv.get_json()


def test_group_success(client, gss_user, mock_ldap_client):
    mock_ldap_client(
        get_group=lambda n, attrs: {
            "groupname": "dummy-group",
            "description": "the dummy-group",
            "mailing_list": "dummy-group@groups.com",
            "url": "www.dummy-group.com",
            "irc": ["#dummy-group"],
        },
    )

    rv = client.get("/v1/groups/dummy-group/")

    expected = {
        "groupname": "dummy-group",
        "description": "the dummy-group",
        "mailing_list": "dummy-group@groups.com",
        "url": "www.dummy-group.com",
        "irc": ["#dummy-group"],
        "uri": "http://localhost/v1/groups/dummy-group/",
    }
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_group_with_mask(client, gss_user, mock_ldap_client):
    mock_ldap_client(
        get_group=lambda n, attrs: {
            "groupname": "dummy-group",
            "description": "the dummy-group",
            "mailing_list": "dummy-group@groups.com",
            "url": "www.dummy-group.com",
            "irc": ["#dummy-group"],
        },
    )

    rv = client.get(
        "/v1/groups/dummy-group/",
        headers={"X-Fields": "{groupname,description,uri}"},
    )

    expected = {
        "groupname": "dummy-group",
        "description": "the dummy-group",
        "uri": "http://localhost/v1/groups/dummy-group/",
    }
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_group_not_found(client, gss_user, mock_ldap_client):
    mock_ldap_client(get_group=lambda n, attrs=None: None)
    rv = client.get("/v1/groups/dummy-group/")
    assert rv.status_code == 404
    rv = client.get("/v1/groups/dummy-group/is-member/anybody")
    assert rv.status_code == 404


def test_group_is_member_true(client, gss_user, mock_ldap_client):
    mock_ldap_client(
        check_membership=lambda groupname, username: True,
        get_group=lambda n, attrs=None: {"cn": n},
    )

    rv = client.get("/v1/groups/admins/is-member/admin")
    assert 200 == rv.status_code
    assert {"result": True} == rv.get_json()


def test_group_is_member_false(client, gss_user, mock_ldap_client):
    mock_ldap_client(
        check_membership=lambda groupname, username: False,
        get_group=lambda n, attrs=None: {"cn": n},
    )

    rv = client.get("/v1/groups/admins/is-member/someone-else")
    assert 200 == rv.status_code
    assert {"result": False} == rv.get_json()


def test_group_starting_with_number(client, gss_user, mock_ldap_client):
    mock_ldap_client(
        get_group=lambda n, attrs: {
            "groupname": "3d-printing-sig",
            "description": "I start with a number",
        },
    )

    rv = client.get("/v1/groups/3d-printing-sig/")

    expected = {
        "groupname": "3d-printing-sig",
        "description": "I start with a number",
        "mailing_list": None,
        "url": None,
        "irc": None,
        "uri": "http://localhost/v1/groups/3d-printing-sig/",
    }
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}
