"""/api/member"""

import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from ...typedef import Location, Role, MediaItem, MediaType, User

members = sanic.Blueprint('member_api', url_prefix='/member')

@members.post('/edit/<action:(name|username|password|email|phone)')
async def edit_member(rqst):
    try:
        member = await User(rqst.raw_args['uid'])
        new = rqst.raw_args['new']
    except KeyError:
        sanic.exceptions.abort(422, 'Missing user info')
    if action='password':
        sanic.exceptions.abort(404)
        # ugh
    await member.edit(action, new)
    return sanic.response.raw(status=204)
