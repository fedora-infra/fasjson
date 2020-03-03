from fasjson.web import errors
from fasjson.web.extensions.flask_ldapconn import get_ldap_conn


def groups():
    get_ldap_conn()
    raise errors.WebApiError('method not implemented', 405, data={'reason': 'method not implemented'})


def group_members(name):
    get_ldap_conn()
    raise errors.WebApiError('method not implemented', 405, data={'reason': 'method not implemented'})
