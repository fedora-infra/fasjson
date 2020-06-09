from flask_restx import Resource

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


@api_v1.route("/search/<search_term>/")
@api_v1.param("search_term", "The term used to find a user or list of users")
@api_v1.response(404, "User not found")
class SearchUsers(Resource):
    @api_v1.doc("search")
    @api_v1.expect(page_request_parser)
    @api_v1.marshal_with(UserModel)
    def get(self, search_term):
        """Fetch users given a search term"""
        args = page_request_parser.parse_args()
        client = ldap_client()
        filters = (
            f"(&(objectClass=fasUser)(!(nsAccountLock=TRUE))(|(username=*{search_term}*)"
            f"(mail=*{search_term}*)(surname=*{search_term}*)(givenname=*{search_term}*)"
            f"(fasIRCNick=*{search_term}*)))"
        )
        sub_dn = "cn=users,cn=accounts"
        res = client.search(
            model=LDAPUserModel,
            filters=filters,
            sub_dn=sub_dn,
            page_size=args.page_size,
            page_number=args.page
        )
        if res is None:
            api_v1.abort(404, "Empty result", search_term=search_term)
        return res.items
