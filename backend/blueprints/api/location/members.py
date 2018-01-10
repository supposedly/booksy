"""/location/members"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

mbrs = sanic.Blueprint('location_members_api', url_prefix='/members')

@mbrs.post('/add')
@uid_get('location', user=True)
@rqst_get('data')
@jwtdec.protected()
async def add_member_to_location(rqst, user, location, data):
    if not user.perms.can_manage_members:
        sanic.exceptions.abort(401, 'Unauthorized to add members')
    return await location.add_member(**userdata)

@mbrs.post('/remove')
@uid_get('location', user=True)
@rqst_get('toRemove')
@jwtdec.protected()
async def remove_member_from_location(rqst, user, location, to_remove):
    if not user.perms.can_manage_members:
        sanic.exceptions.abort(401, 'Unauthorized to remove members')
    await location.remove_member(to_remove)
    return sanic.response.raw('', 204)
