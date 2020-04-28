from .client import LDAP


# Re-use connections
__ldap = {}


def get_client(uri, basedn, login, **kwargs):
    global __ldap
    if login not in __ldap:
        __ldap[login] = LDAP(uri, basedn, **kwargs)
    return __ldap[login]
