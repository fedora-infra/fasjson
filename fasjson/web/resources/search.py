from flask_restx import Resource

from fasjson.web.utils.ipa import ldap_client
from fasjson.web.utils.pagination import page_request_parser
from .base import Namespace
from .users import UserModel


api_v1 = Namespace("search", description="Search related operations")


@api_v1.route("/users/<search_term>/")
@api_v1.param("search_term", "The term used to find a user or list of users")
class SearchUsers(Resource):
    @api_v1.doc("search")
    @api_v1.expect(page_request_parser)
    @api_v1.paged_marshal_with(UserModel, "v1.search_users")
    def get(self, search_term):
        """Fetch users given a search term"""
        args = page_request_parser.parse_args()
        if args.page_size and args.page_size > 40:
            api_v1.abort(
                403,
                "Page size cannot be greater than 40 when searching.",
                page_size=args.page_size,
            )
        if len(search_term) < 3:
            api_v1.abort(
                403,
                "Search term must be at least 3 characters long.",
                search_term=search_term,
            )
        client = ldap_client()
        result = client.search_users(
            search_term=search_term,
            page_size=args.page_size,
            page_number=args.page
        )
        return result
