from flask import url_for
from flask_restx import Resource, fields

from fasjson.web.utils.ipa import ldap_client
from .base import Namespace


api_v1 = Namespace("me", description="Information about the connected user")

MeModel = api_v1.model(
    "Me",
    {
        "dn": fields.String,
        "username": fields.String,
        "service": fields.String,
        "uri": fields.String,
    },
)


@api_v1.route("/")
class Me(Resource):
    @api_v1.doc("whoami")
    @api_v1.marshal_with(MeModel)
    def get(self):
        """Fetch the connected user"""
        client = ldap_client()
        result = client.whoami()
        if "username" in result:
            result["uri"] = url_for(
                "v1.users_user", username=result["username"], _external=True
            )
        return result
