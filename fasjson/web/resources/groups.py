from flask_restx import Resource, fields

from fasjson.web.utils.ldap import ldap_client
from fasjson.web.utils.pagination import (
    page_request_parser,
    paged_marshal_with,
)
from .base import Namespace


api_v1 = Namespace("groups", description="Groups related operations")

GroupModel = api_v1.model(
    "Group",
    {
        "name": fields.String(),
        "uri": fields.Url("v1.groups_group", absolute=True),
    },
)
MemberModel = api_v1.model(
    "Member",
    {
        "username": fields.String(),
        "uri": fields.Url("v1.users_user", absolute=True),
    },
)


@api_v1.route("/")
class GroupList(Resource):
    @api_v1.doc("list_groups")
    @paged_marshal_with(GroupModel, "v1.groups_group_list")
    def get(self):
        """List all groups"""
        args = page_request_parser.parse_args()
        client = ldap_client()
        result = client.get_groups(
            page_size=args.page_size, page_number=args.page
        )
        return result


@api_v1.route("/<name:name>/")
@api_v1.param("name", "The group name")
@api_v1.response(404, "Group not found")
class Group(Resource):
    @api_v1.doc("get_group")
    @api_v1.marshal_with(GroupModel)
    def get(self, name):
        """Fetch a group given their name"""
        client = ldap_client()
        res = client.get_group(name)
        if res is None:
            api_v1.abort(404, "Group not found", name=name)
        return res


@api_v1.route("/<name:name>/members/")
@api_v1.param("name", "The group name")
@api_v1.response(404, "Group not found")
class GroupMembers(Resource):
    @api_v1.doc("get_group_members")
    @paged_marshal_with(MemberModel, "v1.groups_group_members")
    def get(self, name):
        """Fetch group members given the group name"""
        args = page_request_parser.parse_args()
        client = ldap_client()

        group = client.get_group(name)
        if group is None:
            api_v1.abort(404, "Group not found", name=name)

        return client.get_group_members(
            name, page_size=args.page_size, page_number=args.page
        )
