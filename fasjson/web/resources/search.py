from flask_restx import Resource

from fasjson.web.utils.ipa import ldap_client
from fasjson.web.utils.pagination import page_request_parser
from .base import Namespace
from .users import UserModel

search_request_parser = page_request_parser.copy()
search_request_parser.add_argument("email", help="The email to search for")
search_request_parser.add_argument(
    "username", help="The username to search for"
)
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
    @api_v1.paged_marshal_with(UserModel, "v1.search_search_users")
    def get(self):
        """Fetch users given a search term"""
        search_args = search_request_parser.parse_args()
        page_number, page_size = self._parse_page_args(search_args)
        self._validate_search_args(search_args)

        client = ldap_client()
        result = client.search_users(
            page_size=page_size, page_number=page_number, **search_args
        )
        return result

    def _parse_page_args(self, search_args):
        """
        A simple function to remove and return the page size and number from the search args.
        Page size:
            - is between 1 and 40
            - is a number
            - defaults to 40 if not provided
        """
        page_number = search_args.pop("page_number")
        page_size = search_args.pop("page_size")
        page_size = 40 if page_size is None else page_size

        if page_size > 40 or page_size == 0:
            api_v1.abort(
                400,
                "Page size must be between 1 and 40 when searching.",
                page_size=page_size,
            )
        return page_number, page_size

    def _validate_search_args(self, search_args):
        """
        A simple function to validate the provided arguments.
        Checks:
            - At least one search term must be provided
            - All provided search terms must be greater than 3 characters in length
        """
        if not any(search_args.values()):
            api_v1.abort(400, "At least one search term must be provided.")
        for search_term, search_value in search_args.items():
            if search_value and len(search_value) < 3:
                api_v1.abort(
                    400,
                    "Search term must be at least 3 characters long.",
                    search_term=search_term,
                    search_value=search_value,
                )
