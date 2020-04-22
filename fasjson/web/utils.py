from flask import current_app

from fasjson.lib import ldaputils


def ldap_client():
    return ldaputils.singleton(
        current_app.config["FASJSON_LDAP_URI"],
        basedn=current_app.config["FASJSON_IPA_BASEDN"],
    )
