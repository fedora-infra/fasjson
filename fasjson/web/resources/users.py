from flask_restx import Resource, fields

from fasjson.lib.ldap.models import UserModel as LDAPUserModel
from fasjson.web.utils.ipa import ldap_client, get_fields_from_ldap_model
from fasjson.web.utils.pagination import page_request_parser
from .base import Namespace


api_v1 = Namespace("users", description="Users related operations")

UserModel = api_v1.model(
    "User",
    get_fields_from_ldap_model(
        LDAPUserModel, "v1.users_user", {"locked": {"default": False}}
    ),
)

UserGroupsModel = api_v1.model(
    "UserGroup",
    {
        "groupname": fields.String(),
        "uri": fields.Url("v1.groups_group", absolute=True),
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
            page_size=args.page_size, page_number=args.page_number
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


@api_v1.route("/<name:username>/groups/")
@api_v1.param("username", "The user name")
@api_v1.response(404, "User not found")
class UserGroups(Resource):
    @api_v1.doc("list_user_groups")
    @api_v1.expect(page_request_parser)
    @api_v1.paged_marshal_with(UserGroupsModel, "v1.users_user_groups")
    def get(self, username):
        """Fetch a user's groups given their username"""
        args = page_request_parser.parse_args()
        client = ldap_client()
        user = client.get_user(username)
        if user is None:
            api_v1.abort(404, "User does not exist", name=username)
        return client.get_user_groups(
            username=username,
            page_size=args.page_size,
            page_number=args.page_number,
        )
