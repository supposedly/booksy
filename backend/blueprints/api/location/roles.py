"""/location/roles"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

mbrs = sanic.Blueprint('location_roles_api', url_prefix='/roles')

@uid_get('role')
@roles.get('/')
@jwtdec.protected()
async def search_roles(rqst, role)


@uid_get('role')
@rqst_get('newRole')
@roles.post('/add')
async def add_role_to_location(rqst):
    if not role.can_manage_roles:
        sanic.exceptions.abort
