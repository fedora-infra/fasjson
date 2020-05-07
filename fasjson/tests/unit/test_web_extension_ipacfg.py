import os
from types import SimpleNamespace
from unittest import mock

import pytest
import dns
import dns.rdtypes.IN.SRV

from fasjson.web.extensions.flask_ipacfg import (
    IPAConfig,
    query_srv,
    sort_prio_weight,
    _mix_weight,
)


TEST_IPACFG = """
[global]
basedn = dc=testing
realm = TESTING
domain = testing
server = ipa.testing
host = fasjson.testing
xmlrpc_uri = https://ipa.testing/ipa/xml
enable_ra = True
"""


@pytest.fixture
def app_with_filtered_config(app, mocker):
    old_config = dict(app.config)
    mocker.patch.dict(app.config, clear=True)
    for key, value in old_config.items():
        if key.startswith("FASJSON_"):
            continue
        app.config[key] = value
    yield app
    app.config = old_config


def _make_dns_answer(records):
    qname = "_ldap._tcp.example.com"
    mocked_records = dns.rrset.from_text_list(
        name=qname,
        rdclass="IN",
        rdtype="SRV",
        ttl=3600,
        text_rdatas=[
            " ".join(
                [
                    str(record.get("priority", 10)),
                    str(record.get("weight", 10)),
                    str(record.get("port", 389)),
                    record["name"],
                ]
            )
            for record in records
        ],
    )
    mocked_answer = dns.resolver.Answer(
        qname,
        dns.rdatatype.SRV,
        rdclass=dns.rdataclass.IN,
        response=SimpleNamespace(
            answer=dns.message.ANSWER,
            find_rrset=lambda *a, **kw: mocked_records,
        ),
    )
    return mocked_answer


def test_ipacfg_delayed_init(mocker):
    init_app = mocker.patch.object(IPAConfig, "init_app")
    IPAConfig(None)
    init_app.assert_not_called()


def test_ipacfg_default_paths(app_with_filtered_config):
    app = app_with_filtered_config
    IPAConfig(app)
    with app.test_request_context("/v1/"):
        try:
            app.preprocess_request()
        except FileNotFoundError:
            # We may be running the testsuite on a host that does not have the IPA
            # config files. It's fine, ignore it.
            if os.path.exists("/etc/ipa/default.conf"):
                raise
        assert (
            app.config["FASJSON_IPA_CONFIG_PATH"] == "/etc/ipa/default.conf"
        )
        assert app.config["FASJSON_IPA_CA_CERT_PATH"] == "/etc/ipa/ca.crt"


def test_ipacfg_delayed_load(tmpdir, app_with_filtered_config):
    app = app_with_filtered_config
    config_path = os.path.join(tmpdir, "ipa.cfg")
    app.config["FASJSON_IPA_CONFIG_PATH"] = config_path
    IPAConfig(app)
    assert "FASJSON_IPA_CONFIG_LOADED" not in app.config
    with app.test_request_context("/v1/"):
        with open(config_path, "w") as ipacfg_file:
            ipacfg_file.write(TEST_IPACFG)
        app.preprocess_request()
        assert app.config["FASJSON_IPA_CONFIG_LOADED"] is True
        assert app.config["FASJSON_IPA_BASEDN"] == "dc=testing"
        assert app.config["FASJSON_IPA_DOMAIN"] == "testing"


def test_default_app(app):
    with app.test_request_context("/v1/"):
        IPAConfig(app)._load_config()
        # This should not crash


def test_already_loaded(mocker, app):
    with app.test_request_context("/v1/"):
        app.preprocess_request()
        assert app.config["FASJSON_IPA_CONFIG_LOADED"] is True
        configparser = mocker.patch(
            "fasjson.web.extensions.flask_ipacfg.configparser"
        )
        IPAConfig(app)._load_config()
        configparser.ConfigParser.assert_not_called()


def test_detect_dns(mocker, app):
    ext = IPAConfig(app)
    mocker.patch(
        "fasjson.web.extensions.flask_ipacfg.query_srv",
        return_value=[
            SimpleNamespace(target="ldap1", port=389),
            SimpleNamespace(target="ldap2", port=389),
        ],
    )
    with app.test_request_context("/v1/"):
        ext._detect_ldap()
    expected = "ldap://ldap1:389 ldap://ldap2:389"
    assert app.config["FASJSON_LDAP_URI"] == expected


def test_dns_query():
    resolver = mock.Mock()
    resolver.query.return_value = _make_dns_answer(
        [
            dict(name="ldap1", priority=30),
            dict(name="ldap2", priority=20, weight=2),
            dict(name="ldap3", priority=20, weight=1),
            dict(name="ldap4", priority=10),
        ]
    )
    result = query_srv("_ldap._tcp.example.com", resolver)
    result_names = [str(r.target) for r in result]
    assert result_names[0] == "ldap4"
    assert result_names[3] == "ldap1"
    assert result_names[1:3] in [["ldap2", "ldap3"], ["ldap3", "ldap2"]]


def test_dns_query_same_prio_same_weight():
    names = ["ldap1", "ldap2", "ldap3"]
    resolver = mock.Mock()
    resolver.query.return_value = _make_dns_answer(
        [{"name": name} for name in names]
    )
    result = query_srv("_ldap._tcp.example.com", resolver)
    result_names = [str(r.target) for r in result]
    assert set(result_names) == set(names)


def test_dns_query_no_record():
    resolver = mock.Mock()
    resolver.query.return_value = _make_dns_answer([])
    result = query_srv("_ldap._tcp.example.com", resolver)
    assert len(result) == 0


def test_dns_query_duplicates():
    result = sort_prio_weight(
        [
            SimpleNamespace(priority=1, target="ldap1"),
            SimpleNamespace(priority=1, target="ldap1"),
        ]
    )
    assert len(result) == 1


def test_mix_weight():
    total = 100
    records = _make_dns_answer(
        [{"name": f"ldap-{idx}", "weight": idx} for idx in range(total)]
    )
    result = _mix_weight(records)
    result_names = [str(r.target) for r in result]
    # Uh, I don't really know how to check for weighted randomness.
    # Let's check it has been shuffled
    assert result_names != [f"ldap-{idx}" for idx in range(total)]
    # And we didn't drop any item
    assert len(result_names) == total
