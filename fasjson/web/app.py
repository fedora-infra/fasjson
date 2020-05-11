import os
from logging.config import dictConfig

from flask import Flask
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import HTTPException
from flask_healthz import healthz

from .apis.v1 import blueprint as blueprint_v1
from .apis.errors import blueprint as blueprint_errors, api as api_errors

from .extensions.flask_gss import FlaskGSSAPI
from .extensions.flask_ipacfg import IPAConfig

from .base_routes import root


class NameConverter(BaseConverter):
    """Limit what a user or group name can look like in the URLs."""

    regex = "[a-zA-Z][a-zA-Z0-9_.-]{0,63}"


def create_app(config=None):
    """See https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/"""

    app = Flask(__name__)

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
    FlaskGSSAPI(app)
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
