from flask_restx import Resource, fields

from fasjson.web.utils.ldap import ldap_client
from fasjson.web.utils.pagination import page_request_parser
from .base import Namespace


api_v1 = Namespace("users", description="Users related operations")

UserModel = api_v1.model(
    "User",
    {
        "username": fields.String(),
        "surname": fields.String(),
        "givenname": fields.String(),
        "emails": fields.List(fields.String()),
        "ircnick": fields.String(),
        "locale": fields.String(),
        "timezone": fields.String(),
        "gpgkeyids": fields.List(fields.String()),
        "creation": fields.DateTime(),
        "locked": fields.Boolean(default=False),
        "uri": fields.Url("v1.users_user", absolute=True),
    },
)


@api_v1.route("/")
class UserList(Resource):
    @api_v1.doc("list_users")
    @api_v1.expect(page_request_parser)
    @api_v1.paged_marshal_with(UserModel, "v1.users_user_list")
    def get(self):
        """List all users"""
        args = page_request_parser.parse_args()
        client = ldap_client()
        result = client.get_users(
            page_size=args.page_size, page_number=args.page
        )
        return result


@api_v1.route("/<name:username>/")
@api_v1.param("username", "The user name")
@api_v1.response(404, "User not found")
class User(Resource):
    @api_v1.doc("get_user")
    @api_v1.marshal_with(UserModel)
    def get(self, username):
        """Fetch a user given their name"""
        client = ldap_client()
        res = client.get_user(username)
        if res is None:
            api_v1.abort(404, "User not found", name=username)
        return res
