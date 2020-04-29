import pytest
import os
import types

from flask.testing import FlaskClient

from fasjson.web.app import app


@pytest.fixture
def test_dir():
    return os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def fixture_dir(test_dir):
    return f"{test_dir}/fixtures"


@pytest.fixture
def app_config(fixture_dir):
    app.config["FASJSON_IPA_CONFIG_PATH"] = f"{fixture_dir}/ipa.default.conf"
    app.config["FASJSON_IPA_CA_CERT_PATH"] = f"{fixture_dir}/ipa.ca.crt"
    app.config["TESTING"] = True


@pytest.fixture
def gss_env(fixture_dir):
    output = {}
    with open(f"{fixture_dir}/fasjson.env") as f:
        for line in f.readlines():
            k, v = line.replace("\n", "").split("=")
            output[k] = v
    return output


class GSSAwareClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        self.gss_env = kwargs.pop("gss_env")
        super().__init__(*args, **kwargs)

    def open(self, *args, **kwargs):
        environ_base = self.gss_env.copy()
        environ_base.update(kwargs.get("environ_base", {}))
        kwargs["environ_base"] = environ_base
        return super().open(*args, **kwargs)


@pytest.fixture
def client(app_config, gss_env):
    app.test_client_class = GSSAwareClient
    with app.test_client(gss_env=gss_env) as client:
        yield client


@pytest.fixture
def anon_client(app_config):
    app.test_client_class = FlaskClient
    with app.test_client() as client:
        yield client


@pytest.fixture
def gss_user(gss_env, mocker):
    creds = mocker.patch("gssapi.Credentials")
    creds.return_value = types.SimpleNamespace(lifetime=10)


@pytest.fixture
def mock_ldap_client(mocker):
    def ldap_client_factory(module_path, **kwargs):
        client = types.SimpleNamespace(**kwargs)
        factory = mocker.patch(f"{module_path}.ldap_client")
        factory.return_value = client
        return client

    return ldap_client_factory
