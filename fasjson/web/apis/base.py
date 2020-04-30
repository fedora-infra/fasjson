import ldap
from flask_restx import Api, abort
from flask_restx.api import SwaggerView
from werkzeug.exceptions import HTTPException


def handle_ldap_local_error(error):
    return ({"message": "LDAP local error", "details": str(error)}, 500)


def handle_ldap_server_error(error):
    return {"message": "LDAP server is down"}, 500


def handle_webserver_error(code):
    """Generate JSON on Apache-generated errors (or whichever webserver is used)."""
    abort(code)


class FasJsonApi(Api):
    def init_app(self, app, **kwargs):
        kwargs.setdefault("add_specs", False)  # We add our own route
        super().init_app(app, **kwargs)
        self.errorhandler(ldap.LOCAL_ERROR)(handle_ldap_local_error)
        self.errorhandler(ldap.SERVER_DOWN)(handle_ldap_server_error)
        self.blueprint.record_once(self._on_blueprint_registration)

    def _on_blueprint_registration(self, state):
        # Add URL rules on the top level app
        self._register_specs_top(state.app)
        self._register_doc_top(state.app)

        # TODO: make sure the following two instructions are not done multiple times when we have
        # multiple API versions.

        # Make the main app's error handler use the API's error handler in order to output JSON
        state.app.register_error_handler(HTTPException, self.handle_error)
        # Register views for the webserver to use so that it outputs JSON too
        state.app.add_url_rule(
            "/errors/<int:code>", view_func=handle_webserver_error
        )

    def _register_specs_top(self, top_level_app):
        endpoint = f"{self.blueprint.name}.specs"
        top_level_app.add_url_rule(
            f"/specs/{self.blueprint.name}.json",
            endpoint=endpoint,
            view_func=SwaggerView.as_view(endpoint, self, [self]),
        )

    def _register_doc_top(self, top_level_app):
        top_level_app.add_url_rule(
            f"/docs/{self.blueprint.name}/",
            f"{self.blueprint.name}.doc",
            self.render_doc,
        )
