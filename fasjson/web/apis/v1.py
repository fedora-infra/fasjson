from flask import Blueprint

from .base import FasJsonApi
from ..resources.me import api_v1 as me
from ..resources.users import api_v1 as users
from ..resources.groups import api_v1 as groups

blueprint = Blueprint("v1", __name__, url_prefix="/v1")
api = FasJsonApi(blueprint, version="1.0")

api.add_namespace(me)
api.add_namespace(users)
api.add_namespace(groups)
