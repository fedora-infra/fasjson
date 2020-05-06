import ldap
from flask_restx import Api
from flask_restx.api import SwaggerView


def handle_ldap_local_error(error):
    return ({"message": "LDAP local error", "details": str(error)}, 500)


def handle_ldap_server_error(error):
    return {"message": "LDAP server is down"}, 500


API_DEFAULTS = {
    "title": "FAS-JSON",
    "description": "The Fedora Accounts System JSON API",
    "license": "GPLv3",
    "license_url": "https://www.gnu.org/licenses/gpl-3.0.html",
    # We add our own route for specs and docs
    "add_specs": False,
    "doc": False,
}


class FasJsonApi(Api):
    def init_app(self, app, **kwargs):
        for key, value in API_DEFAULTS.items():
            kwargs.setdefault(key, value)

        super().init_app(app, **kwargs)

        self.errorhandler(ldap.LOCAL_ERROR)(handle_ldap_local_error)
        self.errorhandler(ldap.SERVER_DOWN)(handle_ldap_server_error)
        self.blueprint.record_once(self._on_blueprint_registration)

    def _on_blueprint_registration(self, state):
        # Add URL rules on the top level app
        self._register_specs_top(state.app)
        self._register_doc_top(state.app)

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
