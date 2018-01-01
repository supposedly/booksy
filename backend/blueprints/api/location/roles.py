"""/location/roles"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

roles = sanic.Blueprint('location_roles_api', url_prefix='/roles')

@uid_get('role')
@roles.get('/')
@jwtdec.protected()
async def search_roles(rqst, role):
    if not role.can_manage_roles:
        sanic.exceptions.abort(403, 'Unauthorized to manage roles')
    sanic.exceptions.abort(404)
    return None


@uid_get('role')
@rqst_get('newRole')
@roles.post('/add')
@jwtdec.protected()
async def add_role_to_location(rqst, role, new_role):
    sanic.exceptions.abort(404)
    if not role.can_manage_roles:
        sanic.exceptions.abort(403, 'Unauthorized to manage roles')
    return None
