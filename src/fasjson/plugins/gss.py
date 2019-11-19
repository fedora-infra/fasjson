#
# Copyright (C) 2019  Christian Heimes <cheimes@redhat.com>
# See COPYING for license
#
"""GSSAPI plugin for Flask
"""
import gssapi
from flask import abort, request


class FlaskGSSAPI:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self._gssapi_check)

    def _gssapi_check(self):
        environ = request.environ
        if environ["wsgi.multithread"]:
            abort(
                400,
                "GSSAPI is not compatible with multi-threaded WSGI servers.",
            )

        ccache = environ.get("KRB5CCNAME")
        if not ccache:
            abort(400, "KRB5CCNAME missing.")
            raise ValueError("KRB5CCNAME missing")

        principal = environ.get("GSS_NAME")
        if not principal:
            abort(400, "GSS_NAME missing.")

        gss_name = gssapi.Name(principal, gssapi.NameType.kerberos_principal)
        try:
            creds = gssapi.Credentials(
                usage="initiate", name=gss_name, store={"ccache": ccache}
            )
        except gssapi.exceptions.GSSError as e:
            abort(403, f"Invalid credentials {e}")
        else:
            if creds.lifetime <= 0:
                abort(401, "Credential lifetime has expired.")
