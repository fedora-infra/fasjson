from flask import Flask, request
from werkzeug.routing import BaseConverter

from . import errors
from .apis import v1
from .response import ApiResponse
from .extensions.flask_gss import FlaskGSSAPI
from .extensions.flask_ipacfg import IPAConfig


app = Flask(__name__)
app.response_class = ApiResponse

# extensions
FlaskGSSAPI(app)
IPAConfig(app)


# converters
class UserGroupConverter(BaseConverter):
    regex = "[a-zA-Z][a-zA-Z0-9_.-]{0,63}"


app.url_map.converters["usergroup"] = UserGroupConverter

# blueprints
app.register_blueprint(v1.app, url_prefix="/v1")


@app.errorhandler(errors.WebApiError)
def handle_error(e):
    return e.get_response()


@app.errorhandler(404)
def handle_error_404(e):
    data = {"path": request.path, "method": request.method}
    e = errors.WebApiError("resource not found", 404, data=data)
    return e.get_response()


@app.errorhandler(500)
def handle_error_500(e):
    original = getattr(e, "original_exception", None)
    data = {
        "path": request.path,
        "method": request.method,
        "exception": str(original),
    }
    e = errors.WebApiError("unexpected internal error", 500, data=data)
    return e.get_response()
