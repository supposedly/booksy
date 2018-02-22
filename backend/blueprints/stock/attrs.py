"""/stock/attrs"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from . import uid_get, rqst_get
from . import Location, Role, MediaType, MediaItem, User
from ...attributes import Perms, Maxes, Locks

attrs = sanic.Blueprint('attr_stock', url_prefix='/attrs')

@attrs.get('/signup-form')
async def serve_signup_form(rqst):
    res = {}
    return sanic.response.json(res)
