import datetime

import ldap
import ldap.filter as ldap_filter #type: ignore
from ldap.controls.pagedresults import SimplePagedResultsControl


__ldap = None


def singleton(uri, trace_level=0, basedn=None):
    global __ldap
    if __ldap is None:
        __ldap = LDAP(uri, trace_level, basedn)
    return __ldap


known_ldap_resp_ctrls = {
    SimplePagedResultsControl.controlType: SimplePagedResultsControl,
}


class Converter:
    def __init__(self, attrname, destname, multivalued=False, missing=None):
        self.attrname = attrname
        self.destname = destname
        self.multivalued = multivalued
        self.missing = missing

    def convert(self, value):
        return value.decode('utf-8')

    def __call__(self, dct):
        if self.attrname not in dct:
            return self.missing
        values = dct[self.attrname]
        if not values:
            return self.missing
        values = [self.convert(v) for v in values]
        if self.multivalued:
            return values
        else:
            return values[0]


class BoolConverter(Converter):
    def convert(self, value):
        value = value.decode('utf-8').upper()
        if value == 'TRUE':
            return True
        if value == 'FALSE':
            return False
        raise ValueError(value)


class GeneralTimeConverter(Converter):
    gentime_fmt = "%Y%m%d%H%M%SZ"

    def convert(self, value):
        value = value.decode("utf-8")
        return datetime.datetime.strptime(value, self.gentime_fmt)


USER_ATTR = [
    Converter("uid", "login"),
    Converter("sn", "surename"),
    Converter("givenName", "givenname"),
    Converter("mail", "mails", multivalued=True),
    Converter("fasIRCNick", "ircnick"),
    Converter("fasLocale", "locale"),
    Converter("fasTimeZone", "timezone"),
    Converter("fasGPGKeyId", "gpgkeyids", multivalued=True),
    GeneralTimeConverter("fasCreationTime", "creationts"),
    BoolConverter("nsAccountLock", "locked", missing=False),
]


class LDAP(object):
    default_basedn = 'dc=example,dc=test'

    def __init__(self, uri, trace_level=0, basedn=None):
        self.basedn = self.default_basedn if not basedn else basedn
        ldap.set_option(ldap.OPT_REFERRALS, 0)
        self.conn = ldap.initialize(uri, trace_level=trace_level)
        self.conn.protocol_version = 3
        self.conn.sasl_interactive_bind_s('', ldap.sasl.sasl({}, 'GSS-SPNEGO'))

    def whoami(self):
        raw = self.conn.whoami_s()
        data = {}
        parts = raw.split('dn: ')[1].split(',')
        data['krbprincipalname'] = parts[0].split('=')[1]
        for part in parts[1:]:
            k, v = part.split('=')
            if not k in data:
                data[k] = []
            data[k].append(v)
        return (raw, data)

    def get_group_members(self, groupname, size=20, cookie=''):
        page_control = SimplePagedResultsControl(True, size=size, cookie=cookie)
        groupname = ldap_filter.escape_filter_chars(groupname)
        dn = f"cn=users,cn=accounts,{self.basedn}"
        filters = (
            "(&"
            f"(memberOf=cn={groupname},cn=groups,cn=accounts,{self.basedn})"
            "(objectClass=person)"
            "(!(nsAccountLock=TRUE))"
            ")"
        )
        scope = ldap.SCOPE_SUBTREE
        attrlist = ['uid']
        output = []

        msgid = self.conn.search_ext(dn, scope, filters, attrlist=attrlist, serverctrls=[page_control])
        if msgid is None:
            return (None, 0, None, output)

        rtype, rdata, rmsgid, serverctrls = self.conn.result3(msgid, resp_ctrl_classes=known_ldap_resp_ctrls)
        for dn, data in rdata:
            output.append(data['uid'][0].decode('utf8'))

        controls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
        if controls:
            ctrl = controls[0]
            if int(ctrl.size) == 0:
              return (rmsgid, 0, None, output)
            if ctrl.cookie:
                return (rmsgid, size, ctrl.cookie, output)
        return (rmsgid, 0, None, output)

    def get_groups(self, size=20, cookie=''):
        page_control = SimplePagedResultsControl(True, size=size, cookie=cookie)
        dn = f"cn=groups,cn=accounts,{self.basedn}"
        filters = r"(|(objectClass=ipausergroup)(objectclass=groupofnames))"
        scope = ldap.SCOPE_SUBTREE
        attrlist = ['cn']
        output = []

        msgid = self.conn.search_ext(dn, scope, filters, attrlist=attrlist, serverctrls=[page_control])
        if msgid is None:
            return (None, 0, None, output)

        rtype, rdata, rmsgid, serverctrls = self.conn.result3(msgid, resp_ctrl_classes=known_ldap_resp_ctrls)
        for dn, data in rdata:
            output.append(data['cn'][0].decode('utf8'))

        controls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
        if controls:
            ctrl = controls[0]
            if int(ctrl.size) == 0:
              return (rmsgid, 0, None, output)
            if ctrl.cookie:
                return (rmsgid, size, ctrl.cookie, output)
        return (rmsgid, 0, None, output)

    def get_user(self, username):
        username = ldap_filter.escape_filter_chars(username)
        dn = f"uid={username},cn=users,cn=accounts,{self.basedn}"
        filters = "(objectClass=person)"
        scope = ldap.SCOPE_BASE
        # attrlist = ["*", "+"]
        attrlist = list(c.attrname for c in USER_ATTR)
        result = self.conn.search_s(dn, scope, filters, attrlist)
        if not result:
            return None
        attrs = result[0][1]
        result = {c.destname: c(attrs) for c in USER_ATTR}
        # result['raw'] = repr(attrs)
        return result
