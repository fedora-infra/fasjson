from ldap.filter import escape_filter_chars

from .converters import (
    Converter,
    GeneralTimeConverter,
    BoolConverter,
    BinaryConverter,
)


class Model:
    primary_key = None
    filters = "(objectClass=*)"
    sub_dn = None
    fields = {}

    @classmethod
    def get_sub_dn_for(cls, name):
        name = escape_filter_chars(name)
        return f"{cls.primary_key}={name},{cls.sub_dn}"

    @classmethod
    def get_ldap_attrs(cls):
        return [converter.ldap_name for converter in cls.fields.values()]

    @classmethod
    def convert_ldap_result(cls, result):
        new_result = {}
        for dest_name, converter in cls.fields.items():
            try:
                existing_value = result[converter.ldap_name]
            except KeyError:
                continue
            new_result[dest_name] = converter.from_ldap(existing_value)
        return new_result


class UserModel(Model):
    primary_key = "uid"
    filters = "(&(objectClass=fasUser)(!(nsAccountLock=TRUE)))"
    sub_dn = "cn=users,cn=accounts"
    fields = {
        "username": Converter("uid"),
        "surname": Converter("sn"),
        "givenname": Converter("givenName"),
        "human_name": Converter("displayName"),
        "emails": Converter("mail", multivalued=True),
        "ircnicks": Converter("fasIRCNick", multivalued=True),
        "locale": Converter("fasLocale"),
        "timezone": Converter("fasTimeZone"),
        "gpgkeyids": Converter("fasGPGKeyId", multivalued=True),
        "certificates": BinaryConverter("userCertificate", multivalued=True),
        "creation": GeneralTimeConverter("fasCreationTime"),
        "locked": BoolConverter("nsAccountLock"),
    }


class SponsorModel(Model):
    primary_key = "memberManager"
    filters = "(&(objectClass=fasUser)(!(nsAccountLock=TRUE)))"
    sub_dn = "cn=users,cn=accounts"
    fields = {
        "sponsors": Converter("memberManager", multivalued=True),
    }


class GroupModel(Model):
    primary_key = "cn"
    filters = "(objectClass=fasGroup)"
    sub_dn = "cn=groups,cn=accounts"
    fields = {"groupname": Converter("cn")}
