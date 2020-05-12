import re


import ldap
from flask import jsonify, url_for, current_app
from flask_healthz import HealthError


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


def readiness():
    """Readiness Health Check"""
    try:
        client = ldap.initialize(current_app.config["FASJSON_LDAP_URI"])
        client.simple_bind_s()
    except ldap.SERVER_DOWN:
        raise HealthError("LDAP server is down")
