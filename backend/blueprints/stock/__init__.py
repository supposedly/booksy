from sanic import Blueprint

from .. import Location, Role, MediaType, MediaItem, User
from .. import uid_get, rqst_get

from .buttons import btn
from .attrs import attrs

stock = Blueprint.group(btn, attrs, url_prefix='/stock')
