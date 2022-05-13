import os
from logging.config import dictConfig

from flask import Flask
from flask.wrappers import Request
from flask_healthz import healthz
from flask_mod_auth_gssapi import FlaskModAuthGSSAPI
from flask_restx import abort
from werkzeug.exceptions import HTTPException
from werkzeug.routing import BaseConverter

from .apis.errors import api as api_errors
from .apis.errors import blueprint as blueprint_errors
from .apis.v1 import blueprint as blueprint_v1
from .base_routes import root
from .extensions.flask_ipacfg import IPAConfig


class NameConverter(BaseConverter):
    """Limit what a user or group name can look like in the URLs."""

    regex = "[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}"


# https://github.com/pallets/flask/issues/4552#issuecomment-1109785314
class AnyJsonRequest(Request):
    def on_json_loading_failed(self, e):
        if e is not None:
            return super().on_json_loading_failed(e)


def create_app(config=None):
    """See https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/"""

    app = Flask(__name__)

    # Don't crash if content-type is not set to application/json.
    # https://github.com/python-restx/flask-restx/issues/422
    app.request_class = AnyJsonRequest

    # Load default configuration
    app.config.from_pyfile("defaults.cfg")

    # Load the optional configuration file
    if "FASJSON_CONFIG_PATH" in os.environ:
        app.config.from_envvar("FASJSON_CONFIG_PATH")

    # Load the config passed as argument
    app.config.update(config or {})

    # Logging
    if app.config.get("LOGGING"):
        dictConfig(app.config["LOGGING"])

    # Extensions
    FlaskModAuthGSSAPI(app, abort=abort)
    IPAConfig(app)

    # URL converters
    app.url_map.converters["name"] = NameConverter

    # Register APIs
    # TODO: consider having only one class per resource and passing the API version from the
    # global g variable as described here:
    # https://flask.palletsprojects.com/en/1.1.x/patterns/urlprocessors/#internationalized-blueprint-urls
    app.register_blueprint(blueprint_v1)
    app.register_blueprint(healthz, url_prefix="/healthz")

    # Handler for webserver errors
    app.register_blueprint(blueprint_errors)
    # Make the main app's error handler use the error API's error handler in order to output JSON
    app.register_error_handler(HTTPException, api_errors.handle_error)

    # Register the root view
    app.add_url_rule("/", endpoint="root", view_func=root)

    return app
