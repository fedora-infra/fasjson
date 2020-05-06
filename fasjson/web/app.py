import re

import ldap

from flask import Flask, jsonify, url_for
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import HTTPException

from .apis.v1 import blueprint as blueprint_v1
from .apis.errors import blueprint as blueprint_errors, api as api_errors

from .extensions.flask_gss import FlaskGSSAPI
from .extensions.flask_ipacfg import IPAConfig

from ..healthz.healthcheck import HealthCheck


app = Flask(__name__)


# Extensions
FlaskGSSAPI(app)
IPAConfig(app)


# URL converters
class NameConverter(BaseConverter):
    regex = "[a-zA-Z][a-zA-Z0-9_.-]{0,63}"


app.url_map.converters["name"] = NameConverter


def ldap_running():
    """Readiness Health Check"""
    try:
        client = ldap.initialize(app.config["FASJSON_LDAP_URI"])
        client.simple_bind_s()
        return True, "OK"
    except ldap.SERVER_DOWN:
        return False, "NOT OK"


def basic_liveness():
    """Liveness Health Check"""
    return True, "OK"


health_check = HealthCheck(app)
health_check.add_check("/healthz/ready", "readiness", ldap_running)
health_check.add_check("/healthz/live", "liveness", basic_liveness)


# TODO: consider having only one class per resource and passing the API version from the global g
# variable as described here:
# https://flask.palletsprojects.com/en/1.1.x/patterns/urlprocessors/#internationalized-blueprint-urls
app.register_blueprint(blueprint_v1)


# Handler for webserver errors
app.register_blueprint(blueprint_errors)
# Make the main app's error handler use the error API's error handler in order to output JSON
app.register_error_handler(HTTPException, api_errors.handle_error)


@app.route("/")
def root():
    blueprints = sorted(
        [name for name in app.blueprints if re.match("^v[0-9]+$", name)],
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
