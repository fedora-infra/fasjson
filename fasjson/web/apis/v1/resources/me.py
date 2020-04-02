import json

import ldap  #type: ignore
from flask import current_app

from fasjson.web import errors, response, utils


def me():
    try:
        l = utils.ldap_client()
        raw, parsed = l.whoami()
    except (ldap.LOCAL_ERROR, ldap.SERVER_DOWN) as e:
        raise errors.WebApiError('LDAP local error', 500, data={'exception': str(e)})
    
    output = {
        'result': {
            'raw': raw,
            'info': parsed
        }
    }
    
    return output, 200
