from flask import Blueprint

from flask_restx import Api, Resource, abort

blueprint = Blueprint("errors", __name__, url_prefix="/errors")
api = Api(blueprint, title="Webserver errors", doc=False, add_specs=False)


@api.route("/<int:code>")
class Error(Resource):
    """Generate JSON on Apache-generated errors (or whichever webserver is used)."""

    def get(self, code):
        abort(code)
