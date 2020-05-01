import ldap

from flask import current_app
from flask_restx import Resource, fields

from .base import Namespace


api_v1 = Namespace(
    "health", description="Information about the application's health"
)

HealthModel = api_v1.model("Health", {"status": fields.String})


class Live(Resource):
    @api_v1.doc("live")
    @api_v1.marshal_with(HealthModel, "v1.health.live")
    def get():
        """Liveness Health Check"""
        return {"status": "OK"}, 200


class Ready(Resource):
    @api_v1.doc("ready")
    @api_v1.marshal_with(HealthModel, "v1.health.ready")
    def get():
        """Readiness Health Check"""
        try:
            client = ldap.initialize(current_app.config["FASJSON_LDAP_URI"])
            client.simple_bind_s()
            return {"status": "OK"}, 200
        except ldap.SERVER_DOWN:
            return {"status": "NOT OK"}, 503
