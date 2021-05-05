from ldap.filter import escape_filter_chars

from .converters import (
    BinaryConverter,
    BoolConverter,
    Converter,
    GeneralTimeConverter,
)


class Model:
    primary_key = None
    filters = "(objectClass=*)"
    sub_dn = None
    fields = {}
    hidden_fields = []

    @classmethod
    def get_sub_dn_for(cls, name):
        name = escape_filter_chars(name)
        return f"{cls.primary_key}={name},{cls.sub_dn}"

    @classmethod
    def get_ldap_attrs(cls):
        return [
            converter.ldap_name
            for key, converter in cls.fields.items()
            if key not in cls.hidden_fields
        ]

    @classmethod
    def attrs_to_ldap(cls, attrs):
        if attrs is None:
            return None
        return [
            cls.fields[name].ldap_name for name in attrs if name in cls.fields
        ]

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
        "sshpubkeys": Converter("ipaSshPubKey", multivalued=True),
        "certificates": BinaryConverter("userCertificate", multivalued=True),
        "creation": GeneralTimeConverter("fasCreationTime"),
        "is_private": BoolConverter("fasIsPrivate"),
        "locked": BoolConverter("nsAccountLock"),
        "memberof": Converter("memberof", multivalued=True),
    }
    hidden_fields = ["memberof"]
    private_fields = [
        "human_name",
        "surname",
        "givenname",
        "ircnicks",
        "locale",
        "timezone",
        "gpgkeyids",
    ]

    @classmethod
    def anonymize(cls, user):
        for attr in cls.private_fields:
            try:
                del user[attr]
            except KeyError:
                continue
        return user


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
    fields = {
        "groupname": Converter("cn"),
        "description": Converter("description"),
        "mailing_list": Converter("fasmailinglist"),
        "url": Converter("fasurl"),
        "irc": Converter("fasircchannel", multivalued=True),
    }


class AgreementModel(Model):
    primary_key = "cn"
    filters = "(&(objectClass=fasAgreement)(ipaEnabledFlag=TRUE))"
    sub_dn = "cn=fasagreements"
    fields = {
        "name": Converter("cn"),
    }
