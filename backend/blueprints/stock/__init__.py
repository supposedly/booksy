from sanic import Blueprint

from .. import Location, Role, MediaType, MediaItem, User
from .. import uid_get

from .buttons import btn

stock = Blueprint.group(btn, url_prefix='/stock')
