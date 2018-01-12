"""/location/roles"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

roles = sanic.Blueprint('location_roles_api', url_prefix='/roles')

@roles.get('/')
@uid_get('perms', 'location')
@jwtdec.protected()
async def all_roles(rqst, perms, location):
    if not perms.can_manage_roles:
        sanic.exceptions.abort(403, "You're not allowed to manage or view roles.")
    return sanic.response.json({"roles": await location.roles()}, status=200)

@roles.post('/add')
@rqst_get('user', 'seq')
@jwtdec.protected()
async def add_role_to_location(rqst, user, name, seq):
    if not user.perms.can_manage_roles:
        sanic.exceptions.abort(403, "You're not allowed to manage roles.")
    await user.location.add_role(name, seq=seq)
