import datetime
from base64 import b64encode


class Converter:
    def __init__(self, ldap_name, multivalued=False):
        self.ldap_name = ldap_name
        self.multivalued = multivalued

    def from_ldap(self, value):
        value = [self.decode(v) for v in value]
        if not self.multivalued:
            value = value[0]
        return value

    def decode(self, value):
        return value.decode("utf-8")


class BoolConverter(Converter):
    def decode(self, value):
        value = super().decode(value).upper()
        if value == "TRUE":
            return True
        if value == "FALSE":
            return False
        raise ValueError(value)


class GeneralTimeConverter(Converter):
    gentime_fmt = "%Y%m%d%H%M%SZ"

    def decode(self, value):
        value = super().decode(value)
        return datetime.datetime.strptime(value, self.gentime_fmt)


class BinaryConverter(Converter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ldap_name = f"{self.ldap_name};binary"

    def decode(self, value):
        return b64encode(value).decode("ascii")
