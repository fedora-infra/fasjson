from flask import current_app, g
from flask_restx import abort, fields
from python_freeipa import ClientMeta

from fasjson.lib.ldap import get_client, converters


def ldap_client():
    print("gss_creds:", repr(g.gss_creds))
    if g.gss_creds is None:
        abort(401)
    return get_client(
        current_app.config["FASJSON_LDAP_URI"],
        basedn=current_app.config["FASJSON_IPA_BASEDN"],
        login=g.username,
        timeout=current_app.config.get("FASJSON_LDAP_TIMEOUT", 30),
    )


def rpc_client():
    print("gss_creds:", repr(g.gss_creds))
    if g.gss_creds is None:
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


def dummy_rpc_call():
    import gssapi
    import requests
    import requests_gssapi

    HOSTNAME = current_app.config["FASJSON_IPA_SERVER"]
    HEADERS = {
        'Referer': f'https://{HOSTNAME}/ipa',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    creds = gssapi.Credentials(name=None, usage="initiate")

    sess = requests.session()
    print(repr(current_app.config["FASJSON_IPA_CA_CERT_PATH"]))
    #sess.verify = "/etc/ipa/ca.crt"
    sess.verify = current_app.config["FASJSON_IPA_CA_CERT_PATH"]
    #sess.verify = True
    sess.auth = requests_gssapi.HTTPSPNEGOAuth(
        opportunistic_auth=True, creds=creds
    )

    res = sess.post(
        f"https://{HOSTNAME}/ipa/session/json",
        headers=HEADERS,
        json={
            "method": "ping",
            "params": [
                [],
                {}
            ]
        }
    )

    return res.json()



