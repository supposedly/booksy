from sanic import Blueprint

from .. import email_verify
from ..typedef import Location, Role, MediaType, MediaItem, User
from ..deco import uid_get, rqst_get

from .api import api
from .stock import stock

bp = Blueprint.group(api, stock)
