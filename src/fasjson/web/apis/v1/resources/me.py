from fasjson.web import errors
from fasjson.web.extensions.flask_ldapconn import get_ldap_conn

def me():
    get_ldap_conn()
    raise errors.WebApiError('method not implemented', 405, data={'reason': 'method not implemented'})
