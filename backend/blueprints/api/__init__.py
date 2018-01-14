from sanic import Blueprint

from .. import Location, Role, MediaType, MediaItem, User
from .. import uid_get, rqst_get

from .location import location
from .media import media
from .member import member
from .signup import signup
from .roles import roles
from .help import help

api = Blueprint.group(location, media, member, signup, roles, help, url_prefix='/api')
