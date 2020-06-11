from flask import Blueprint

from .base import FasJsonApi
from ..resources.me import api_v1 as me
from ..resources.users import api_v1 as users
from ..resources.groups import api_v1 as groups
from ..resources.certs import api_v1 as certs
from ..resources.search import api_v1 as search

blueprint = Blueprint("v1", __name__, url_prefix="/v1")
api = FasJsonApi(blueprint, version="1.0")

api.add_namespace(me)
api.add_namespace(users)
api.add_namespace(groups)
api.add_namespace(certs)
api.add_namespace(search)
