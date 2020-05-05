from flask import current_app, g
from flask_restx import abort, fields
from python_freeipa import ClientMeta

from fasjson.lib.ldap import get_client, converters


def ldap_client():
    if g.username is None:
        abort(401)
    return get_client(
        current_app.config["FASJSON_LDAP_URI"],
        basedn=current_app.config["FASJSON_IPA_BASEDN"],
        login=g.username,
        timeout=current_app.config.get("FASJSON_LDAP_TIMEOUT", 30),
    )


def rpc_client():
    if g.username is None:
        abort(401)
    client = ClientMeta(
        current_app.config["FASJSON_IPA_SERVER"],
        verify_ssl=current_app.config["FASJSON_IPA_CA_CERT_PATH"],
    )
    client.login_kerberos()
    return client


def get_fields_from_ldap_model(ldap_model, endpoint, field_args=None):
    field_args = field_args or {}
    result = {}

    for attr, ldap_converter in ldap_model.fields.items():
        if isinstance(ldap_converter, converters.BoolConverter):
            field = fields.Boolean
        elif isinstance(ldap_converter, converters.GeneralTimeConverter):
            field = fields.DateTime
        else:
            field = fields.String

        field = field(**field_args.get(attr, {}))

        if ldap_converter.multivalued:
            field = fields.List(field)

        result[attr] = field

    result["uri"] = fields.Url(endpoint, absolute=True)

    return result
