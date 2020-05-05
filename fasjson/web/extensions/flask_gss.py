import os

import gssapi
from flask import request, g
from flask_restx import abort


class FlaskGSSAPI:
    def __init__(self, app):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self._gssapi_check)

    def _gssapi_check(self):
        g.gss_name = g.gss_creds = g.principal = g.username = None

        environ = request.environ
        if environ["wsgi.multithread"]:
            abort(
                500,
                "GSSAPI is not compatible with multi-threaded WSGI servers.",
            )
        ccache = environ.get("KRB5CCNAME")
        if not ccache:
            return  # Maybe the endpoint is not protected, stop here
        # The LDAP library will look for the cache in the process' environment variables
        os.environ["KRB5CCNAME"] = ccache

        principal = environ.get("GSS_NAME")
        if not principal:
            return  # Maybe the endpoint is not protected, stop here

        gss_name = gssapi.Name(principal, gssapi.NameType.kerberos_principal)
        try:
            creds = gssapi.Credentials(
                usage="initiate", name=gss_name, store={"ccache": ccache}
            )
        except gssapi.exceptions.GSSError as e:
            abort(
                403,
                "Invalid credentials",
                codes={
                    "maj": e.maj_code,
                    "min": e.min_code,
                    "routine": e.routine_code,
                    "supplementary": e.supplementary_code,
                },
            )
        if creds.lifetime <= 0:
            abort(401, "Credential lifetime has expired")

        g.gss_name = gss_name
        g.gss_creds = creds
        g.principal = gss_name.display_as(gssapi.NameType.kerberos_principal)
        g.username = g.principal.split("@")[0]
