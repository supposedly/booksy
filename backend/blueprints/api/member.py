"""/api/member"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

members = sanic.Blueprint('member_api', url_prefix='/member')

@rqst_get('user', 'new')
@members.post('/edit')
@jwtdec.protected()
async def edit_member(rqst, member, new, action):
    if action == 'password':
        sanic.exceptions.abort(404)
        # ugh
    await member.edit(action, new)
    return sanic.response.raw(status=204)
