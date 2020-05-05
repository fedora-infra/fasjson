from flask import current_app, g
from flask_restx import abort

from fasjson.lib.ldap import get_client


def ldap_client():
    if g.gss_name is None:
        abort(401)
    return get_client(
        current_app.config["FASJSON_LDAP_URI"],
        basedn=current_app.config["FASJSON_IPA_BASEDN"],
        login=g.gss_name,
        timeout=current_app.config.get("FASJSON_LDAP_TIMEOUT", 30),
    )
