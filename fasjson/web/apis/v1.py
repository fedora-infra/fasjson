from flask import Blueprint

from ..resources.certs import api_v1 as certs
from ..resources.groups import api_v1 as groups
from ..resources.me import api_v1 as me
from ..resources.search import api_v1 as search
from ..resources.users import api_v1 as users
from .base import FasJsonApi


blueprint = Blueprint("v1", __name__, url_prefix="/v1")
api = FasJsonApi(blueprint, version="1.0")

api.add_namespace(me)
api.add_namespace(users)
api.add_namespace(groups)
api.add_namespace(certs)
api.add_namespace(search)
