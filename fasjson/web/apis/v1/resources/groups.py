import ldap  #type: ignore

from fasjson.web import errors
from fasjson.web.extensions.flask_ldapconn import get_ldap_conn


def groups():
    try:
        conn = get_ldap_conn()
        res = list(conn.get_groups())
    except ldap.LOCAL_ERROR as e:
        raise errors.WebApiError('LDAP local error', 500, data={'exception': str(e)})
    
    if len(res) == 0:
        raise errors.WebApiError('0 groups found', 404)
    
    output = {
        'result': {
            'data': res
        }
    }
    
    return output, 200


def group_members(name):
    try:
        conn = get_ldap_conn()
        res = list(conn.get_group_members(name))
    except ldap.LOCAL_ERROR as e:
        raise errors.WebApiError('LDAP local error', 500, data={'exception': str(e)})
    
    if len(res) == 0:
        raise errors.WebApiError('0 members found', 404, data={'group': name})
    
    output = {
        'result': {
            'data': res
        }
    }
    
    return output, 200
