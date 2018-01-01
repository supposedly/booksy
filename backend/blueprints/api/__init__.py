from sanic import Blueprint

from .. import Location, Role, MediaType, MediaItem, User
from .. import uid_get, rqst_get

from .location import location
from .media import media
from .member import members
from .signup import signup
from .role_attrs import roles

api = Blueprint.group(location, media, members, signup, roles, url_prefix='/api')
