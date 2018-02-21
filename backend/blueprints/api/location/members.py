"""/location/members"""
import asyncpg
try:
    import bcrypt
except ModuleNotFoundError: # means I'm testing
    pass
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from . import uid_get, rqst_get
from . import Location, Role, MediaType, MediaItem, User

mbrs = sanic.Blueprint('location_members_api', url_prefix='/members')

@mbrs.get('/')
@rqst_get('cont')
@uid_get('location')
@jwtdec.protected()
async def serve_location_members(rqst, location, cont):
    return sanic.response.json(await location.members(cont=int(cont)))

@mbrs.get('/info')
@uid_get('perms')
@rqst_get('check')
@jwtdec.protected()
async def serve_specific_member(rqst, to_check, perms):
    if not perms.can_manage_accounts:
        sanic.exceptions.abort(403, "You aren't allowed to view member info.")
    user = await User(to_check, rqst.app)
    return sanic.response.json({'member': user.to_dict()}, status=200)

@mbrs.post('/add')
@uid_get('location', 'perms')
@rqst_get('member') # member to create
@jwtdec.protected()
async def add_member_to_location(rqst, member, location, perms):
    """
    Addition of a given member.
    Creates an account for them with the chosen default password and
    roles, in the same location the requester is in.
    """
    try:
        username, rid, fullname, password = [member[i] for i in ('username', 'rid', 'name', 'password')]
    except KeyError:
        sanic.exceptions.abort(422, 'Missing required attributes.')
    if not perms.can_manage_accounts:
        sanic.exceptions.abort(403, "You aren't allowed to add members.")
    pwhash = await rqst.app.aexec(rqst.app.ppe, bcrypt.hashpw, password.encode('utf-8'), bcrypt.gensalt(12))
    try:
        new = sanic.response.json(await location.add_member(username=username, pwhash=pwhash, rid=rid, fullname=fullname), status=200)
    except asyncpg.exceptions.UniqueViolationError:
        sanic.exceptions.abort(409, 'This username is already taken.')
    return new

@mbrs.post('/add/batch')
@uid_get('location', 'perms')
@jwtdec.protected()
async def add_members_from_csv(rqst, location, perms):
    """
    Batch addition of members.
    Likely will not be implemented.
    """
    if not perms.can_manage_members:
        sanic.exceptions.abort(401, "You aren't allowed to add members.")
    data = rqst.files.get(data, None)
    if data is None: # using conditional instead of try/except bc the data itself might also be null instead of just not present
        sanic.exceptions.abort(422, "No file given!")
    rqst.app.add_task(location.members_from_csv(data))
    return sanic.response.json('', status=202) # (accepted for further processing)

@mbrs.post('/remove')
@uid_get('location', 'perms')
@rqst_get('member')
@jwtdec.protected()
async def remove_member_from_location(rqst, to_remove, location, perms):
    """
    Removal of a given member.
    Undecided as to whether this should delete the table row entirely.
    (Which would make sense, no? Since a member can't be assigned 'no'
    location?)
    
    UPDATE: Decided on yes
    """
    if not perms.can_manage_accounts:
        sanic.exceptions.abort(401, "You aren't allowed to remove members.")
    await location.remove_member(uid=to_remove)
    return sanic.response.raw('', 204)
