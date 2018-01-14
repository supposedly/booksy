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
        sanic.exceptions.abort(403, "You aren't allowed to modify roles.")
    return sanic.response.json({"roles": await location.roles()}, status=200)

@roles.post('/add')
@rqst_get('user', 'name', 'seqs')
@jwtdec.protected()
async def add_role_to_location(rqst, user, name, kws):
    if not user.perms.can_manage_roles:
        sanic.exceptions.abort(403, "You aren't allowed to modify roles.")
    if name.lower() in ('admin', 'organizer', 'subscriber'):
        sanic.exceptions.abort(403, "That name is reserved.")
    role = await user.location.add_role(name=name, kws=kws)
    return sanic.response.json({'rid': role.rid}, status=200)
