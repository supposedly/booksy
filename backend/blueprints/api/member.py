"""/api/member"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

member = sanic.Blueprint('member_api', url_prefix='/member')

@member.get('/notifications')
@rqst_get('location', 'username')
@jwtdec.protected()
async def get_notifs(rqst, location, username):
    user = await User.from_identifiers(username, location, app=rqst.app)
    return sanic.response.json(await user.notifs(), status=200)

@member.get('/suggest')
@uid_get('location', 'recent')
@jwtdec.protected()
async def get_recent(rqst, location, recent):
    return sanic.response.json({'items': await location.search(genre=recent, max_results=3)}, status=200)

@member.get('/checked-out')
@uid_get()
@jwtdec.protected()
async def get_user_items(rqst, user):
    return sanic.response.json(await user.items(), status=200)

@member.get('/held')
@uid_get()
@jwtdec.protected()
async def get_user_holds(rqst, user):
    return sanic.response.json(await user.held(), status=200)

@member.post('/edit')
@rqst_get('user', 'username', 'fullname', 'rid') # note that this here is the user TO EDIT, not the one sending the request
@jwtdec.protected()
async def edit_member(rqst, user, username, fullname, rid):
    await user.edit(username, rid, fullname)
    return sanic.response.raw(b'', status=204)

@member.get('/check-perms')
@uid_get('perms')
@jwtdec.protected()
async def check_perms(rqst, perms):
    return sanic.response.json({'can_edit_media': perms.can_manage_media}, status=200)
