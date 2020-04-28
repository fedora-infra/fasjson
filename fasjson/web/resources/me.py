from flask_restx import Resource, fields

from fasjson.web.utils.ldap import ldap_client
from .base import Namespace


api_v1 = Namespace("me", description="Information about the connected user")

MeModel = api_v1.model(
    "Me",
    {
        "dn": fields.String,
        "username": fields.String,
        "uri": fields.Url("v1.users_user", absolute=True),
    },
)


@api_v1.route("/")
class Me(Resource):
    @api_v1.doc("get_me")
    @api_v1.marshal_with(MeModel)
    def get(self):
        """Fetch the connected user"""
        client = ldap_client()
        return client.whoami()
