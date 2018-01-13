"""/location/members"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

mbrs = sanic.Blueprint('location_members_api', url_prefix='/members')

@mbrs.get('/')
@rqst_get('cont')
@uid_get('location')
@jwtdec.protected()
async def serve_location_members(rqst, location, cont):
    return sanic.response.json(await location.members(cont=int(cont)))

@mbrs.post('/add')
@uid_get('location', 'perms')
@rqst_get('data')
@jwtdec.protected()
async def add_member_to_location(rqst, location, perms, data):
    """
    Addition of a given member.
    Creates an account for them with the chosen default password and
    roles, in the same location the requester is in.
    """
    if not perms.can_manage_members:
        sanic.exceptions.abort(401, 'Unauthorized to add members.')
    return sanic.response.json(await location.add_member(**userdata), status=202)

@mbrs.post('/add/batch')
@uid_get('location', 'perms')
@rqst_get('data')
@jwtdec.protected()
async def add_members_from_csv(rqst, location, perms, data):
    """
    Batch addition of members.
    Likely will not be implemented.
    
    If it is, location.from_csv() will probably just place
    csv.read() in a ProcessPoolExecutor, then when that's
    finished will iterate through the resulting object
    and add each item to the DB one by one.
    """
    if not perms.can_manage_members:
        sanic.exceptions.abort(401, 'Unauthorized to add members.')
    rqst.app.add_task(location.from_csv(data))
    return sanic.response.json('', status=202)

@mbrs.post('/remove')
@uid_get('location', 'perms')
@rqst_get('toRemove')
@jwtdec.protected()
async def remove_member_from_location(rqst, location, perms, to_remove):
    """
    Removal of a given member.
    Undecided as to whether this should delete the table row entirely.
    (Which would make sense, no? Since a member can't be assigned no
    location?)
    """
    if not perms.can_manage_members:
        sanic.exceptions.abort(401, 'Unauthorized to remove members.')
    await location.remove_member(to_remove)
    return sanic.response.raw('', 204)
