import json
from datetime import datetime, timezone


def test_user_success(client, gss_user, mock_ldap_client):
    data = {
        # "creation": "Mon, 09 Mar 2020 10:32:03 GMT",
        "creation": datetime(2020, 3, 9, 10, 32, 3, tzinfo=timezone.utc),
        "givenname": "",
        "gpgkeyids": None,
        # "ircnick": "",
        # "locale": "",
        "locked": False,
        "username": "admin",
        "emails": ["admin@example.test"],
        "surname": "Administrator",
        # "timezone": "",
    }
    mock_ldap_client("fasjson.web.resources.users", get_user=lambda u: data)

    rv = client.get("/v1/users/admin/")

    expected = data.copy()
    expected["creation"] = data["creation"].isoformat()
    expected["ircnick"] = expected["locale"] = expected["timezone"] = None
    expected["uri"] = "http://localhost/v1/users/admin/"
    assert 200 == rv.status_code
    assert {"result": expected} == json.loads(rv.data)


def test_user_error(client, gss_user, mock_ldap_client):
    mock_ldap_client("fasjson.web.resources.users", get_user=lambda u: None)

    rv = client.get("/v1/users/admin/")
    res = json.loads(rv.data)

    assert 404 == rv.status_code
    assert res == {
        "name": "admin",
        "message": (
            "User not found. You have requested this URI [/v1/users/admin/] "
            "but did you mean /v1/users/<name:username>/ or /v1/users/ ?"
        ),
    }
