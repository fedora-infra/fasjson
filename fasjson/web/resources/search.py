from flask_restx import Resource

from fasjson.web.utils.ipa import ldap_client
from fasjson.web.utils.pagination import page_request_parser
from .base import Namespace
from .users import UserModel

search_request_parser = page_request_parser.copy()
search_request_parser.add_argument(
    "username", help="The username to search for"
)
search_request_parser.add_argument("email", help="The email to search for")
search_request_parser.add_argument(
    "ircnick", help="The ircnick to search for"
)
search_request_parser.add_argument(
    "givenname", help="The first name to search for"
)
search_request_parser.add_argument(
    "surname", help="The surname to search for"
)


api_v1 = Namespace("search", description="Search related operations")


@api_v1.route("/users/")
class SearchUsers(Resource):
    @api_v1.doc("search")
    @api_v1.expect(search_request_parser)
    @api_v1.response(400, "Validation Error")
    @api_v1.paged_marshal_with(UserModel, "v1.search_users")
    def get(self):
        """Fetch users given a search term"""
        search_args = search_request_parser.parse_args()
        page_size = search_args.pop("page_size", 40)
        page_number = search_args.pop("page_number")
        if page_size and page_size > 40:
            api_v1.abort(
                400,
                "Page size cannot be greater than 40 when searching.",
                page_size=page_size,
            )
        if not any(search_args.values()):
            api_v1.abort(400, "At least one search term must be provided")
        for search_term, search_value in search_args.items():
            if search_value and len(search_value) < 3:
                api_v1.abort(
                    400,
                    "Search term must be at least 3 characters long.",
                    search_term=search_term,
                    search_value=search_value,
                )
        client = ldap_client()
        result = client.search_users(
            page_size=page_size, page_number=page_number, **search_args
        )
        return result
