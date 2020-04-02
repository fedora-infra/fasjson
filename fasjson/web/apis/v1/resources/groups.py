import ldap  #type: ignore
from flask import request, g, current_app

from fasjson.web import errors, utils


def groups():
    size = int(request.args.get('results_per_page', 20))
    cookie = request.headers.get('X-FasJson-Cookie', '')
    msgid = request.headers.get('X-Fasjson-Previous-Msgid')

    l = utils.ldap_client()
    while True:
        try:
            rmsgid, rsize, rcookie, rdata = l.get_groups(size=size, cookie=cookie)
        except ldap.LOCAL_ERROR as e:
            raise errors.WebApiError('LDAP local error', 500, data={'exception': str(e)})
        if msgid is None:
            break
        if int(msgid) != int(rmsgid):
            break

    if len(rdata) == 0:
        raise errors.WebApiError('0 groups found', 404)

    c = rcookie.decode() if rcookie else None
    output = {
        'result': {
            'data': rdata,
            'size': rsize
        }
    }
    headers = {'X-FasJson-MsgId': rmsgid}
    if c:
        headers['X-FasJson-Cookie'] = c
    
    return output, 200, headers


def group_members(name):
    size = int(request.args.get('results_per_page', 20))
    cookie = request.headers.get('X-FasJson-Cookie', '')
    msgid = request.headers.get('X-Fasjson-Previous-Msgid')
    
    l = utils.ldap_client()
    while True:
        try:
            rmsgid, rsize, rcookie, rdata = l.get_group_members(name, size=size, cookie=cookie)
        except ldap.LOCAL_ERROR as e:
            raise errors.WebApiError('LDAP local error', 500, data={'exception': str(e)})
        if msgid is None:
            break
        if int(msgid) != int(rmsgid):
            break

    if len(rdata) == 0:
        raise errors.WebApiError('0 groups found', 404)

    c = rcookie.decode() if rcookie else None
    output = {
        'result': {
            'data': rdata,
            'size': rsize
        }
    }
    headers = {'X-FasJson-MsgId': rmsgid}
    if c:
        headers['X-FasJson-Cookie'] = c
    
    return output, 200, headers
