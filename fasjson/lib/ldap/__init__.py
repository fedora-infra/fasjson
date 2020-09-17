from .client import LDAP


def get_client(uri, basedn, login, **kwargs):
    return LDAP(uri, basedn, **kwargs)
