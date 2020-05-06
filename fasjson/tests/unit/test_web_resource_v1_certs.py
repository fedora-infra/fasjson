from functools import partial

import pytest
from python_freeipa.exceptions import BadRequest


@pytest.fixture
def mock_rpc_client(mock_ipa_client):
    yield partial(mock_ipa_client, "fasjson.web.resources.certs", "rpc")


def _get_cert_rpc_data(cert_id):
    return {
        "result": {
            "certificate": "dummmy+cert/+=",
            "serial_number": cert_id,
            "serial_number_hex": "0xC",
            "subject": "CN=dummy,O=EXAMPLE.TEST",
            "issuer": "CN=Certificate Authority,O=EXAMPLE.TEST",
            "valid_not_before": "Tue May 05 06:22:53 2020 UTC",
            "valid_not_after": "Fri May 06 06:22:53 2022 UTC",
            "sha1_fingerprint": "8d:8d:41:6a:ae:8d:95:c5:5f:19:85:6c:16:cc:2f:d0:b0:82:42:c7",
            "sha256_fingerprint": (
                "c4:d7:c8:47:2e:41:16:57:b6:5d:d7:94:ae:d1:a4:66:97:b1:e9:7f:04:"
                "8f:1f:c3:fb:44:e8:89:30:3f:1a:30"
            ),
            "revoked": False,
            "owner_user": ["dummy"],
            "cacn": "ipa",
            "certificate_chain": [
                {"__base64__": "dummmy+cert/+="},
                {"__base64__": "dummmy+ca+cert"},
            ],
        },
        "value": cert_id,
        "summary": None,
    }


def _get_cert_api_output(cert_id):
    return {
        "cacn": "ipa",
        "certificate": "dummmy+cert/+=",
        "certificate_chain": ["dummmy+cert/+=", "dummmy+ca+cert"],
        "issuer": "CN=Certificate Authority,O=EXAMPLE.TEST",
        "revoked": False,
        "san_other": None,
        "san_other_kpn": None,
        "san_other_upn": None,
        "serial_number": cert_id,
        "serial_number_hex": "0xC",
        "sha1_fingerprint": "8d:8d:41:6a:ae:8d:95:c5:5f:19:85:6c:16:cc:2f:d0:b0:82:42:c7",
        "sha256_fingerprint": (
            "c4:d7:c8:47:2e:41:16:57:b6:5d:d7:94:ae:d1:a4:66:97:b1:e9:7f:04:8f:"
            "1f:c3:fb:44:e8:89:30:3f:1a:30"
        ),
        "subject": "CN=dummy,O=EXAMPLE.TEST",
        "valid_not_after": "Fri, 06 May 2022 06:22:53 -0000",
        "valid_not_before": "Tue, 05 May 2020 06:22:53 -0000",
        "uri": f"http://localhost/v1/certs/{cert_id}/",
    }


def test_cert_success(client, gss_user, mock_rpc_client):
    data = _get_cert_rpc_data(42)
    mock_rpc_client(cert_show=lambda cert_id: data)

    rv = client.get("/v1/certs/42/")

    expected = _get_cert_api_output(42)
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}


def test_cert_404(client, gss_user, mock_rpc_client, mocker):
    mock_rpc_client(
        cert_show=mocker.Mock(
            side_effect=BadRequest(message="Error message", code=4301)
        )
    )
    rv = client.get("/v1/certs/42/")
    assert 404 == rv.status_code
    assert rv.get_json() == {
        "message": "Certificate not found",
        "serial_number": 42,
        "server_message": "Error message",
    }


def test_cert_error(client, gss_user, mock_rpc_client, mocker):
    mock_rpc_client(
        cert_show=mocker.Mock(
            side_effect=BadRequest(message="Error message", code=4242)
        )
    )
    rv = client.get("/v1/certs/42/")
    assert 400 == rv.status_code
    assert rv.get_json() == {
        "message": "Error message",
        "code": 4242,
        "source": "RPC",
    }


def test_cert_post_success(client, gss_user, mock_rpc_client, mocker):
    data = _get_cert_rpc_data(42)
    rpc_client = mock_rpc_client(cert_request=mocker.Mock(return_value=data))
    rv = client.post("/v1/certs/", data={"csr": "dummy-csr", "user": "dummy"})
    expected = _get_cert_api_output(42)
    assert 200 == rv.status_code
    assert rv.get_json() == {"result": expected}
    rpc_client.cert_request.assert_called_once_with("dummy-csr", "dummy")
