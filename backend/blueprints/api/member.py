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
@uid_get()
@jwtdec.protected()
async def get_recent(rqst, user):
    return sanic.response.json({'items': await user.location.search(genre=user.recent, max_results=5)}, status=200)

@members.get('/checked-out')
@uid_get)(
@jwtdec.protected()
async def get_user_items(rqst, user):
    return sanic.response.json(await user.items(), status=200)

@members.post('/edit/<action:(password|name)>')
@rqst_get('user', 'new')
@jwtdec.protected()
async def edit_member(rqst, user, new, action):
    sanic.exceptions.abort(501, "Left unimplemented for FBLA demo.")
    #####
    await user.edit(action, new)
    return sanic.response.raw(status=204)
