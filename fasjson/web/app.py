import os
import re
from logging.config import dictConfig

from flask import Flask, jsonify, url_for, current_app
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import HTTPException

from .apis.v1 import blueprint as blueprint_v1
from .apis.errors import blueprint as blueprint_errors, api as api_errors

from .extensions.flask_gss import FlaskGSSAPI
from .extensions.flask_ipacfg import IPAConfig


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

    # Handler for webserver errors
    app.register_blueprint(blueprint_errors)
    # Make the main app's error handler use the error API's error handler in order to output JSON
    app.register_error_handler(HTTPException, api_errors.handle_error)

    # Register the root view
    app.add_url_rule("/", endpoint="root", view_func=root)

    return app


def root():
    blueprints = sorted(
        [
            name
            for name in current_app.blueprints
            if re.match("^v[0-9]+$", name)
        ],
        key=lambda name: int(name[1:]),
    )
    apis = [
        {
            "version": int(name[1:]),
            "uri": url_for(f"{name}.root", _external=True),
            "specs": url_for(f"{name}.specs", _external=True),
            "docs": url_for(f"{name}.doc", _external=True),
        }
        for name in blueprints
    ]
    return jsonify({"message": "Welcome to FASJSON", "apis": apis})
