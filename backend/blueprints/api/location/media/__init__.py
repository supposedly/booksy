"""/api/location/media"""
from sanic import Blueprint

from .. import Location, Role, MediaType, MediaItem, User
from .. import uid_get, rqst_get

from .root import root
from .genres import genres
from .types import types

media = Blueprint.group(genres, types, root, url_prefix='/media')
