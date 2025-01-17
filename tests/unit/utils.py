from datetime import datetime, timezone


def get_user_ldap_data(name):
    return {
        "certificates": None,
        "creation": datetime(2020, 3, 9, 10, 32, 3, tzinfo=timezone.utc),
        "givenname": "",
        "gpgkeyids": None,
        "sshpubkeys": None,
        "locked": False,
        "username": name,
        "emails": [f"{name}@example.test"],
        "surname": name,
        "human_name": name,
        "is_private": False,
        "github_username": name,
        "gitlab_username": name,
        "pronouns": ["they/them/theirs"],
        "rhbzemail": f"{name}@rhbz_example.test",
        "website": f"{name}.example.com",
        "rssurl": f"{name}.example.com/feed",
        "websites": [f"{name}.example.com"],
        "rssurls": [f"{name}.example.com/feed"],
    }


def get_user_api_output(name):
    data = get_user_ldap_data(name)
    data["creation"] = data["creation"].isoformat()
    data["ircnicks"] = data["locale"] = data["timezone"] = None
    data["uri"] = f"http://localhost/v1/users/{name}/"
    return data
