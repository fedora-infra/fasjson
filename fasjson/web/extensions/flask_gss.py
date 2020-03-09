import gssapi #type: ignore
from flask import request, abort

from fasjson.web import errors


class FlaskGSSAPI(object):
    def __init__(self, app):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self._gssapi_check)

    def _gssapi_check(self):
        environ = request.environ
        if environ['wsgi.multithread']:
            raise errors.WebApiError('GSSAPI is not compatible with multi-threaded WSGI servers.',
                400, data={'request.environ.name': 'wsgi.multithread'})

        ccache = environ.get('KRB5CCNAME')
        if not ccache:
            raise errors.WebApiError('KRB5CCNAME missing',
                500, data={'request.environ.KRB5CCNAME': 'KRB5CCNAME'})

        principal = environ.get('GSS_NAME')
        if not principal:
            raise errors.WebApiError('KRB5CCNAME missing',
                500, data={'request.environ.name': 'GSS_NAME'})

        gss_name = gssapi.Name(principal, gssapi.NameType.kerberos_principal)
        try:
            creds = gssapi.Credentials(
                usage='initiate', name=gss_name, store={'ccache': ccache}
            )
        except gssapi.exceptions.GSSError as e:
            raise errors.WebApiError('Invalid credentials',
                403,
                data={
                    'codes': {
                        'maj': e.maj_code,
                        'min': e.min_code,
                        'routine': e.routine_code,
                        'supplementary': e.supplementary_code
                    }
                })
        else:
            if creds.lifetime <= 0:
                raise errors.WebApiError('Credential lifetime has expired', 401)

