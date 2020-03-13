import ldap #type: ignore

from flask import current_app

from fasjson.web import errors
from fasjson.lib import ldaputils


def user(username):
    l = ldaputils.singleton(current_app.config['FASJSON_LDAP_URI'])

    try:
        res = l.get_user(username)
    except ldap.LOCAL_ERROR as e:
        raise errors.WebApiError('LDAP local error', 500, data={'exception': str(e)})
    
    if not res:
        raise errors.WebApiError('user not found', 404, data={'username': username}) 
    output = {
        'result': res
    }
    
    return output, 200