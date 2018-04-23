from sanic import Blueprint

from .. import email_verify
from ..typedef import get_location as Location, get_role as Role, get_mtype as MediaType, get_media_item as MediaItem, get_user as User
from ..deco import uid_get, rqst_get

from .api import api
from .stock import stock

bp = Blueprint.group(api, stock)
