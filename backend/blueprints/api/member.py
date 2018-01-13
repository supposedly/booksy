"""/api/member"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

members = sanic.Blueprint('member_api', url_prefix='/member')

@members.get('/notifications')
@uid_get()
@jwtdec.protected()
async def get_notifs(rqst, user):
    return sanic.response.json(await user.notifs(), status=200)

@members.get('/suggest')
@uid_get('location', 'recent')
@jwtdec.protected()
async def get_recent(rqst, location, recent):
    return sanic.response.json({'items': await location.search(genre=recent, max_results=3)}, status=200)

@members.get('/checked-out')
@uid_get()
@jwtdec.protected()
async def get_user_items(rqst, user):
    return sanic.response.json(await user.items(), status=200)

@members.post('/edit')
@rqst_get('user', 'username', 'fullname', 'rid') # note that this here is the user TO EDIT, not the one sending the request
@jwtdec.protected()
async def edit_member(rqst, user, username, fullname, rid):
    await user.edit(username, rid, fullname)
    return sanic.response.raw(b'', status=204)
