import ldap  # type: ignore

from fasjson.web import errors, utils


def me():
    try:
        ldap_client = utils.ldap_client()
        raw, parsed = ldap_client.whoami()
    except (ldap.LOCAL_ERROR, ldap.SERVER_DOWN) as e:
        raise errors.WebApiError(
            "LDAP local error", 500, data={"exception": str(e)}
        )

    output = {"result": {"raw": raw, "info": parsed}}

    return output, 200
