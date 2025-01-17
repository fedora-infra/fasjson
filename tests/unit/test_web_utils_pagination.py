import pytest

from fasjson.lib.ldap.client import LDAPResult
from fasjson.web.resources.groups import GroupModel
from fasjson.web.utils.pagination import add_page_data, paged_marshal


@pytest.fixture
def ldap_result():
    return LDAPResult(
        items=[
            {
                "groupname": "group1",
                "description": "the group1 group",
                "mailing_list": "group1@groups.com",
                "url": "www.group1.com",
                "irc": ["#group1"],
                "discussion_url": "https://discussion.test/group1",
            }
        ],
        total=2,
        page_number=1,
        page_size=1,
    )


@pytest.fixture
def page_output():
    return {
        "total_results": 2,
        "page_size": 1,
        "page_number": 1,
        "total_pages": 2,
        "next_page": "http://localhost/?page_size=1&page_number=2",
    }


def test_paged_marshal(app, ldap_result, page_output):
    with app.test_request_context("/"):
        output = paged_marshal(ldap_result, GroupModel)

    expected = {
        "groupname": "group1",
        "description": "the group1 group",
        "mailing_list": "group1@groups.com",
        "url": "www.group1.com",
        "irc": ["#group1"],
        "uri": "http://localhost/v1/groups/group1/",
        "discussion_url": "https://discussion.test/group1",
    }

    assert output == {
        "result": [expected],
        "page": page_output,
    }


def test_paged_marshal_with_mask_header(app, ldap_result, page_output):
    with app.test_request_context("/", headers={"X-Fields": "{groupname,mailing_list}"}):
        output = paged_marshal(ldap_result, GroupModel)

    expected = {
        "groupname": "group1",
        "mailing_list": "group1@groups.com",
    }
    assert output == {
        "result": [expected],
        "page": page_output,
    }


def test_paged_marshal_with_mask_arg(app, ldap_result, page_output):
    with app.test_request_context("/"):
        output = paged_marshal(ldap_result, GroupModel, mask="{groupname,mailing_list}")

    expected = {
        "groupname": "group1",
        "mailing_list": "group1@groups.com",
    }
    assert output == {
        "result": [expected],
        "page": page_output,
    }


def test_add_page_data_last_page(app, ldap_result):
    ldap_result.page_number = 2
    output = {}
    with app.test_request_context("/"):
        add_page_data(output, ldap_result, GroupModel)

    assert output["page"] == {
        "total_results": 2,
        "page_size": 1,
        "page_number": 2,
        "total_pages": 2,
    }


def test_add_page_data_existing_qs(app, ldap_result):
    with app.test_request_context("/?foo=bar"):
        output = paged_marshal(ldap_result, GroupModel)

    expected_next_page = "http://localhost/?foo=bar&page_size=1&page_number=2"
    assert output["page"]["next_page"] == expected_next_page
