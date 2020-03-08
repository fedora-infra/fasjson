import json

import ldap  #type: ignore

from fasjson.web import errors, response
from fasjson.web.extensions.flask_ldapconn import get_ldap_conn


def me():
    try:
        conn = get_ldap_conn()
        res = conn.whoami()
    except ldap.LOCAL_ERROR as e:
        raise errors.WebApiError('LDAP local error', 500, data={'exception': str(e)})
    output = {
        'result': {
            'raw': res,
            'info': parse(res)
        }
    }
    return response.ApiResponse(json.dumps(output, sort_keys=True, indent=4), 200)


def parse(s):
    data = {}
    parts = s.split('dn: ')[1].split(',')
    data['krbprincipalname'] = parts[0].split('=')[1]
    for part in parts[1:]:
        k, v = part.split('=')
        if not k in data:
            data[k] = []
        data[k].append(v)
    return data
