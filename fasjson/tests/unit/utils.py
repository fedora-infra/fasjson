from datetime import datetime, timezone


def get_user_ldap_data(name):
    return {
        "certificates": None,
        "creation": datetime(2020, 3, 9, 10, 32, 3, tzinfo=timezone.utc),
        "givenname": "",
        "gpgkeyids": None,
        "locked": False,
        "username": name,
        "emails": [f"{name}@example.test"],
        "surname": name,
        "human_name": name,
    }


def get_user_api_output(name):
    data = get_user_ldap_data(name)
    data["creation"] = data["creation"].isoformat()
    data["ircnicks"] = data["locale"] = data["timezone"] = None
    data["uri"] = f"http://localhost/v1/users/{name}/"
    return data
