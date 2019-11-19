#
# Copyright (C) 2019  Christian Heimes <cheimes@redhat.com>
# See COPYING for license
#
"""LDAP connection plugin
"""
import datetime

from flask import abort, current_app, g

import ldap
import ldap.filter as ldap_filter
import ldap.sasl


SASL_GSS = ldap.sasl.sasl({}, "GSS-SPNEGO")
# SASL_GSS = ldap.sasl.sasl({}, "GSSAPI")


def get_ldap_conn():
    if not hasattr(g, "_ldap_conn"):
        g._ldap_conn = LDAPConn()
    return g._ldap_conn


class Converter:
    def __init__(self, attrname, destname, multivalued=False, missing=None):
        self.attrname = attrname
        self.destname = destname
        self.multivalued = multivalued
        self.missing = missing

    def convert(self, value):
        return value.decode("utf-8")

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
        value = value.decode("utf-8").upper()
        if value == "TRUE":
            return True
        if value == "FALSE":
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


class LDAPConn:
    def __init__(self):
        self._app = current_app
        self._conn = self._ldap_connect()

    def _ldap_connect(self):
        conn = ldap.initialize(current_app.config["LDAP_URI"])
        conn.sasl_interactive_bind_s("", SASL_GSS)
        return conn

    @property
    def basedn(self):
        return self._app.config["IPA_BASEDN"]

    def get_groups(self):
        dn = f"cn=groups,cn=accounts,{self.basedn}"
        filters = "(|(objectClass=ipausergroup)(objectclass=groupofnames))"
        scope = ldap.SCOPE_ONELEVEL
        attrlist = ["cn"]
        for dn, attrs in self._conn.search_s(dn, scope, filters, attrlist):
            yield attrs["cn"][0].decode("utf-8")

    def get_group_members(self, groupname):
        groupname = ldap_filter.escape_filter_chars(groupname)
        dn = f"cn=users,cn=accounts,{self.basedn}"
        filters = (
            "(&"
            f"(memberOf=cn={groupname},cn=groups,cn=accounts,{self.basedn})"
            "(objectClass=person)"
            "(!(nsAccountLock=TRUE))"
            ")"
        )
        scope = ldap.SCOPE_ONELEVEL
        attrlist = ["uid"]
        result = self._conn.search_s(dn, scope, filters, attrlist)
        if not result:
            abort(404, description=f"Group '{groupname}' not found.")
        for dn, attrs in result:
            yield attrs["uid"][0].decode("utf-8")

    def get_user(self, username):
        username = ldap_filter.escape_filter_chars(username)
        dn = f"uid={username},cn=users,cn=accounts,{self.basedn}"
        filters = "(objectClass=person)"
        scope = ldap.SCOPE_BASE
        # attrlist = ["*", "+"]
        attrlist = list(c.attrname for c in USER_ATTR)
        result = self._conn.search_s(dn, scope, filters, attrlist)
        if not result:
            abort(404, f"User '{username}' not found.")
        attrs = result[0][1]
        result = {c.destname: c(attrs) for c in USER_ATTR}
        # result['raw'] = repr(attrs)
        return result

    def whoami(self):
        return self._conn.whoami_s()
