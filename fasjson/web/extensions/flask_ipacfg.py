import configparser
import random
import operator

import dns.resolver
import dns.rdatatype
from dns.exception import DNSException
from flask import current_app


class IPAConfig:
    prefix = "FASJSON_IPA"

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if "FASJSON_IPA_CONFIG_PATH" not in app.config:
            app.config.setdefault(
                "FASJSON_IPA_CONFIG_PATH", "/etc/ipa/default.conf"
            )
        if "FASJSON_IPA_CA_CERT_PATH" not in app.config:
            app.config.setdefault(
                "FASJSON_IPA_CA_CERT_PATH", "/etc/ipa/ca.crt"
            )
        try:
            self._load_config(app)
        except FileNotFoundError:
            pass  # The config will be loaded on request by _detect_ldap
        app.before_request(self._detect_ldap)

    def _load_config(self, app=None):
        _app = app
        if _app is None:
            _app = current_app
        if _app.config.get("FASJSON_IPA_CONFIG_LOADED", False):
            return
        p = configparser.ConfigParser()
        with open(_app.config["FASJSON_IPA_CONFIG_PATH"]) as f:
            p.read_file(f)

        _app.config.setdefault(
            "FASJSON_IPA_BASEDN", p.get("global", "basedn")
        )
        _app.config.setdefault(
            "FASJSON_IPA_DOMAIN", p.get("global", "domain")
        )
        _app.config.setdefault("FASJSON_IPA_REALM", p.get("global", "realm"))
        _app.config.setdefault(
            "FASJSON_IPA_SERVER", p.get("global", "server", fallback=None)
        )
        _app.config.setdefault("FASJSON_IPA_CONFIG_LOADED", True)

    def _detect_ldap(self) -> None:
        # Load the config if it wasn't loaded before
        self._load_config()
        domain = current_app.config["FASJSON_IPA_DOMAIN"]
        servers = []
        try:
            answers = query_srv(f"_ldap._tcp.{domain}")
        except DNSException:
            servers.append(
                "ldap://" + current_app.config["FASJSON_IPA_SERVER"]
            )
        else:
            for answer in answers:
                server = str(answer.target).rstrip(".")
                servers.append(f"ldap://{server}:{answer.port}")
        current_app.config["FASJSON_LDAP_URI"] = " ".join(servers)


def _mix_weight(records):
    """Weighted population sorting for records with same priority
    """
    # trivial case
    if len(records) <= 1:
        return records

    # Optimization for common case: If all weights are the same (e.g. 0),
    # just shuffle the records, which is about four times faster.
    if all(rr.weight == records[0].weight for rr in records):
        random.shuffle(records)
        return records

    noweight = 0.01  # give records with 0 weight a small chance
    result = []
    records = set(records)
    while len(records) > 1:
        # Compute the sum of the weights of those RRs. Then choose a
        # uniform random number between 0 and the sum computed (inclusive).
        urn = random.uniform(0, sum(rr.weight or noweight for rr in records))
        # Select the RR whose running sum value is the first in the selected
        # order which is greater than or equal to the random number selected.
        acc = 0.0
        for rr in records.copy():
            acc += rr.weight or noweight
            if acc >= urn:
                records.remove(rr)
                result.append(rr)

    # randomness makes it hard to check for coverage in these next 2 lines
    if records:  # pragma: no cover
        result.append(records.pop())  # pragma: no cover

    return result


def sort_prio_weight(records):
    """RFC 2782 sorting algorithm for SRV and URI records

    RFC 2782 defines a sorting algorithms for SRV records, that is also used
    for sorting URI records. Records are sorted by priority and than randomly
    shuffled according to weight.

    This implementation also removes duplicate entries.
    """
    # order records by priority
    records = sorted(records, key=operator.attrgetter("priority"))

    # remove duplicate entries
    uniquerecords = []
    seen = set()
    for rr in records:
        # A SRV record has target and port, URI just has target.
        target = (rr.target, getattr(rr, "port", None))
        if target not in seen:
            uniquerecords.append(rr)
            seen.add(target)

    # weighted randomization of entries with same priority
    result = []
    sameprio = []
    for rr in uniquerecords:
        # add all items with same priority in a bucket
        if not sameprio or sameprio[0].priority == rr.priority:
            sameprio.append(rr)
        else:
            # got different priority, shuffle bucket
            result.extend(_mix_weight(sameprio))
            # start a new priority list
            sameprio = [rr]
    # add last batch of records with same priority
    if sameprio:
        result.extend(_mix_weight(sameprio))
    return result


def query_srv(qname, resolver=None, **kwargs):
    """Query SRV records and sort reply according to RFC 2782

    :param qname: query name, _service._proto.domain.
    :return: list of dns.rdtypes.IN.SRV.SRV instances
    """
    if resolver is None:
        resolver = dns.resolver
    answer = resolver.query(qname, rdtype=dns.rdatatype.SRV, **kwargs)
    return sort_prio_weight(answer)
