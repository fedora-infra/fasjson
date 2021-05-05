from fasjson.lib.ldap.models import GroupModel as LDAPGroupModel
from fasjson.lib.ldap.models import UserModel as LDAPUserModel
from fasjson.web.utils.ipa import (
    get_attrs_from_mask,
    get_fields_from_ldap_model,
    ldap_client,
)
from fasjson.web.utils.pagination import page_request_parser
from flask_restx import Resource, fields

from .base import Namespace

api_v1 = Namespace("groups", description="Groups related operations")

GroupModel = api_v1.model(
    "Group", get_fields_from_ldap_model(LDAPGroupModel, "v1.groups_group"),
)

MemberModel = api_v1.model(
    "Member",
    get_fields_from_ldap_model(LDAPUserModel, "v1.users_user"),
    mask="{username,uri}",
)

SponsorModel = api_v1.model(
    "Sponsor",
    get_fields_from_ldap_model(LDAPUserModel, "v1.users_user"),
    mask="{username,uri}",
)


@api_v1.route("/")
class GroupList(Resource):
    @api_v1.doc("list_groups")
    @api_v1.expect(page_request_parser)
    @api_v1.paged_marshal_with(GroupModel)
    def get(self):
        """List all groups"""
        args = page_request_parser.parse_args()
        client = ldap_client()
        result = client.get_groups(
            attrs=get_attrs_from_mask(GroupModel),
            page_size=args.page_size,
            page_number=args.page_number,
        )
        return result


@api_v1.route("/<name:groupname>/")
@api_v1.param("groupname", "The group name")
@api_v1.response(404, "Group not found")
class Group(Resource):
    @api_v1.doc("get_group")
    @api_v1.marshal_with(GroupModel)
    def get(self, groupname):
        """Fetch a group given their name"""
        client = ldap_client()
        res = client.get_group(
            groupname, attrs=get_attrs_from_mask(GroupModel)
        )
        if res is None:
            api_v1.abort(404, "Group not found", groupname=groupname)
        return res


@api_v1.route("/<name:groupname>/members/")
@api_v1.param("groupname", "The group name")
@api_v1.response(404, "Group not found")
class GroupMembers(Resource):
    @api_v1.doc("list_group_members")
    @api_v1.expect(page_request_parser)
    @api_v1.paged_marshal_with(MemberModel)
    def get(self, groupname):
        """Fetch group members given the group name"""
        args = page_request_parser.parse_args()
        client = ldap_client()

        group = client.get_group(groupname)
        if group is None:
            api_v1.abort(404, "Group not found", groupname=groupname)

        return client.get_group_members(
            groupname,
            attrs=get_attrs_from_mask(MemberModel),
            page_size=args.page_size,
            page_number=args.page_number,
        )


@api_v1.route("/<name:groupname>/sponsors/")
@api_v1.param("groupname", "The group name")
@api_v1.response(404, "Group not found")
class GroupSponsors(Resource):
    @api_v1.doc("list_group_sponsors")
    @api_v1.marshal_with(SponsorModel)
    def get(self, groupname):
        """Fetch group sponsors given the group name"""
        client = ldap_client()

        group = client.get_group(groupname)
        if group is None:
            api_v1.abort(404, "Group not found", groupname=groupname)

        return client.get_group_sponsors(
            groupname, attrs=get_attrs_from_mask(SponsorModel)
        )


@api_v1.route("/<name:groupname>/is-member/<name:username>")
@api_v1.param("groupname", "The group name")
@api_v1.param("username", "The user name")
@api_v1.response(404, "Group not found")
class IsMember(Resource):
    @api_v1.doc("check_membership")
    @api_v1.marshal_with(fields.Boolean())
    def get(self, groupname, username):
        """Check whether a user is a member of the group"""
        client = ldap_client()

        group = client.get_group(groupname)
        if group is None:
            api_v1.abort(404, "Group not found", groupname=groupname)

        result = client.check_membership(groupname, username)
        return result
