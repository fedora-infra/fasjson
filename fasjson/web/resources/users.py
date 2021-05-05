from fasjson.lib.ldap.models import GroupModel as LDAPGroupModel
from fasjson.lib.ldap.models import UserModel as LDAPUserModel
from fasjson.web.utils.ipa import (
    get_attrs_from_mask,
    get_fields_from_ldap_model,
    ldap_client,
)
from fasjson.web.utils.pagination import page_request_parser
from flask import g
from flask_restx import Resource, fields

from .base import Namespace

api_v1 = Namespace("users", description="Users related operations")

UserModel = api_v1.model(
    "User",
    get_fields_from_ldap_model(
        LDAPUserModel, "v1.users_user", {"locked": {"default": False}}
    ),
)


def _maybe_anonymize(user):
    if user.get("is_private", False) and g.username != user["username"]:
        user = LDAPUserModel.anonymize(user)
    return user


@api_v1.route("/")
class UserList(Resource):
    @api_v1.doc("list_users")
    @api_v1.expect(page_request_parser)
    @api_v1.paged_marshal_with(UserModel)
    def get(self):
        """List all users"""
        args = page_request_parser.parse_args()
        client = ldap_client()
        result = client.get_users(
            attrs=get_attrs_from_mask(UserModel),
            page_size=args.page_size,
            page_number=args.page_number,
        )
        result.items = [_maybe_anonymize(user) for user in result.items]
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
        res = client.get_user(username, attrs=get_attrs_from_mask(UserModel))
        if res is None:
            api_v1.abort(404, "User not found", name=username)
        res = _maybe_anonymize(res)
        return res


UserGroupsModel = api_v1.model(
    "UserGroup",
    get_fields_from_ldap_model(LDAPGroupModel, "v1.groups_group"),
    mask="{groupname,uri}",
)


@api_v1.route("/<name:username>/groups/")
@api_v1.param("username", "The user name")
@api_v1.response(404, "User not found")
class UserGroups(Resource):
    @api_v1.doc("list_user_groups")
    @api_v1.expect(page_request_parser)
    @api_v1.paged_marshal_with(UserGroupsModel)
    def get(self, username):
        """Fetch a user's groups given their username"""
        args = page_request_parser.parse_args()
        client = ldap_client()
        user = client.get_user(username)
        if user is None:
            api_v1.abort(404, "User does not exist", name=username)
        return client.get_user_groups(
            username=username,
            attrs=get_attrs_from_mask(UserGroupsModel),
            page_size=args.page_size,
            page_number=args.page_number,
        )


UserAgreementsModel = api_v1.model(
    "UserAgreement", {"name": fields.String()},
)


@api_v1.route("/<name:username>/agreements/")
@api_v1.param("username", "The user name")
@api_v1.response(404, "User not found")
class UserAgreements(Resource):
    @api_v1.doc("list_user_agreements")
    @api_v1.expect(page_request_parser)
    @api_v1.paged_marshal_with(UserAgreementsModel)
    def get(self, username):
        """Fetch a user's agreements given their username"""
        args = page_request_parser.parse_args()
        client = ldap_client()
        user = client.get_user(username)
        if user is None:
            api_v1.abort(404, "User does not exist", name=username)
        return client.get_user_agreements(
            username=username,
            page_size=args.page_size,
            page_number=args.page_number,
        )
