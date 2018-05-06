from sanic import Blueprint

from .. import Location, Role, MediaType, MediaItem, User
from .. import uid_get, rqst_get
from .. import email_verify

from .help import help
from .location import location
from .media import media
from .member import mbr as member
# from .signup import signup
from .roles import roles
from .root import root

api = Blueprint.group(help, location, media, member, roles, root, url_prefix='/api')
