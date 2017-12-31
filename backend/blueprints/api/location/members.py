"""/location/members"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

mbrs = sanic.Blueprint('location_members_api', url_prefix='/members')

@uid_get('location', user=True)
@mbrs.post('/add')
@jwtdec.protect()
async def add_member_to_location(rqst, user, location, role):
    try:
        userdata = rqst.form['data']
    except KeyError:
        sanic.exceptions.abort(422, 'No user data given')
    if not user.perms.can_manage_members:
        sanic.exceptions.abort(401, 'Unauthorized to add members')
    return await location.add_member(**userdata)

@uid_get('location', user=True)
@mbrs.post('/remove')
@jwtdec.protect()
async def remove_member_from_location(rqst, user, location, role)
    try:
        to_remove = rqst.form['toRemove']
    except KeyError:
        sanic.exceptions.abort(422, 'No user data given')
    if not user.perms.can_manage_members:
        sanic.exceptions.abort(401, 'Unauthorized to remove members')
    await location.remove_member(toRemove)
    return sanic.response.raw('', 204)
