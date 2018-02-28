from sanic import Blueprint

from .. import Location, Role, MediaType, MediaItem, User
from .. import uid_get, rqst_get

from .buttons import btn
# There were two other files here previously :/

stock = Blueprint.group(btn, url_prefix='/stock')
