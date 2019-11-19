#
# Copyright (C) 2019  Christian Heimes <cheimes@redhat.com>
# See COPYING for license
#
"""Read-only REST-like API for Fedora Account System
"""
import flask
from werkzeug.routing import BaseConverter

from .plugins.gss import FlaskGSSAPI
from .plugins.ipacfg import IPAConfig
from .plugins.ldapconn import get_ldap_conn


app = flask.Flask(__name__)
FlaskGSSAPI(app)
IPAConfig(app)


class UserGroupConverter(BaseConverter):
    regex = "[a-zA-Z][a-zA-Z0-9_.-]{0,63}"


app.url_map.converters["usergroup"] = UserGroupConverter


@app.route("/")
def index():
    conn = get_ldap_conn()
    return conn.whoami()


@app.route("/groups")
def groups():
    conn = get_ldap_conn()
    return flask.jsonify(list(conn.get_groups()))


@app.route("/group/<usergroup:groupname>")
def group(groupname):
    conn = get_ldap_conn()
    return flask.jsonify(list(conn.get_group_members(groupname)))


@app.route("/user/<usergroup:username>")
def user(username):
    conn = get_ldap_conn()
    return flask.jsonify(conn.get_user(username))
