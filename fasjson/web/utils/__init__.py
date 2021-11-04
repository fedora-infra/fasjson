from fasjson.lib.ldap.models import UserModel as LDAPUserModel
from flask import g


def maybe_anonymize(user):
    if user.get("is_private", False) and g.username != user["username"]:
        user = LDAPUserModel.anonymize(user)
    return user
