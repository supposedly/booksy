from sanic import Blueprint

from .. import Location, Role, MediaType, MediaItem, User
from .. import uid_get, rqst_get

from .media import media
from .edit import edit
from .root import root
from .roles import roles
from .members import mbrs as members

location = Blueprint.group(media, edit, members, root, roles, url_prefix='/location')
