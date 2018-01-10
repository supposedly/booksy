"""/location/roles"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

roles = sanic.Blueprint('location_roles_api', url_prefix='/roles')

@roles.get('/')
@uid_get()
@jwtdec.protected()
async def search_roles(rqst, user):
    if not user.perms.can_manage_roles:
        sanic.exceptions.abort(403, 'Unauthorized to manage roles')
    sanic.exceptions.abort(404)
    return None


@roles.post('/add')
@rqst_get('user', 'seq')
@jwtdec.protected()
async def add_role_to_location(rqst, user, seq):
    if not user.perms.can_manage_roles:
        sanic.exceptions.abort(403, 'Unauthorized to manage roles')
    new_role = Role.from_seq(seq)
