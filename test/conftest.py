import pytest
import os

from src.fasjson.web.app import app


@pytest.fixture
def test_dir():
    return os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def fixture_dir(test_dir):
    return f'{test_dir}/fixtures'


@pytest.fixture
def app_config(fixture_dir):
    app.config['FASJSON_IPA_CONFIG_PATH'] = f'{fixture_dir}/ipa.default.conf'
    app.config['FASJSON_IPA_CA_CERT_PATH'] = f'{fixture_dir}/ipa.ca.crt'


@pytest.fixture
def client(app_config):
    with app.test_client() as client:
        yield client


@pytest.fixture
def gss_env(fixture_dir):
    output = {}
    with open(f'{fixture_dir}/fasjson.env') as f:
        for line in f.readlines():
            k, v = line.replace('\n', '').split('=')
            output[k] = v
    return output
