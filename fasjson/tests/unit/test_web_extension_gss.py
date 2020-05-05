import pytest
from flask import g
from werkzeug.exceptions import InternalServerError

from fasjson.web.extensions.flask_gss import FlaskGSSAPI


def test_gssapi_delayed_init(mocker):
    init_app = mocker.patch.object(FlaskGSSAPI, "init_app")
    FlaskGSSAPI(None)
    init_app.assert_not_called()


def test_gssapi_multithread(app):
    with app.test_request_context("/v1/", multithread=True):
        with pytest.raises(InternalServerError):
            app.preprocess_request()


def test_gssapi_no_krb5ccname(app):
    with app.test_request_context("/v1/"):
        app.preprocess_request()
        assert g.principal is None
        assert g.username is None


def test_gssapi_no_username(app):
    with app.test_request_context(
        "/v1/", environ_base={"KRB5CCNAME": "/tmp/ignore"}
    ):
        app.preprocess_request()
        assert g.principal is None
        assert g.username is None
