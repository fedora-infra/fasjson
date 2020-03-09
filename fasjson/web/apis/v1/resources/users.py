import ldap #type: ignore

from fasjson.web import errors
from fasjson.web.extensions.flask_ldapconn import get_ldap_conn


def user(username):
    try:
        conn = get_ldap_conn()
        res = conn.get_user(username)
    except ldap.LOCAL_ERROR as e:
        raise errors.WebApiError('LDAP local error', 500, data={'exception': str(e)})
    
    if not res:
        raise errors.WebApiError('user not found', 404, data={'username': username})
    
    output = {
        'result': res
    }
    
    return output, 200