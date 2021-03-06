from sanic import Blueprint

from .. import Location, Role, MediaType, MediaItem, User
from .. import uid_get, rqst_get
from .. import email_verify

from .media import media
from .root import root
from .roles import roles
from .members import mbrs as members

location = Blueprint.group(media, members, root, roles, url_prefix='/location')
