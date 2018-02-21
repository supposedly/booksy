"""/api/member"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from . import uid_get, rqst_get
from . import Location, Role, MediaType, MediaItem, User

member = sanic.Blueprint('member_api', url_prefix='/member')

@member.get('/notifications')
@rqst_get('location', 'username')
@jwtdec.protected()
async def get_notifs(rqst, location, username):
    """
    Serves the user's notifications -- overdue items, readied holds, etc.
    """
    user = await User.from_identifiers(username, location, app=rqst.app)
    return sanic.response.json(await user.notifs(), status=200)

@member.get('/suggest')
@uid_get('location', 'recent')
@jwtdec.protected()
async def get_recent(rqst, location, recent):
    """
    Serves what's shown in the 'based on your most-recent checkout'
    section of the 'Find Media' page, given a genre to match for.
    """
    return sanic.response.json({'items': await location.search(genre=recent, max_results=2)}, status=200)

@member.get('/checked-out')
@uid_get()
@jwtdec.protected()
async def get_user_items(rqst, user):
    """
    Serves user's checked-out items.
    """
    return sanic.response.json(await user.items(), status=200)

@member.get('/held')
@uid_get()
@jwtdec.protected()
async def get_user_holds(rqst, user):
    """
    Serves user's currently-active holds.
    """
    return sanic.response.json(await user.held(), status=200)

@member.post('/clear-hold')
@rqst_get('user', 'item')
@jwtdec.protected()
async def clear_hold(rqst, user, item):
    """
    Clears a hold the user has on an item.
    """
    await user.clear_hold(item)
    return sanic.response.raw(b'', status=204)

@member.post('/edit')
@rqst_get('user', 'member') # i.e. ('requester', 'user to edit')
@jwtdec.protected()
async def edit_member(rqst, user, member):
    """
    Endpoint for editing user information. Works for both 
    """
    if not (user.uid == member or user.can_manage_accounts):
        sanic.exceptions.abort(403, "You aren't allowed to modify member info.")
    changing = await User(member['user_id'], rqst.app)
    if user.perms.raw < changing.perms.raw:
        sanic.exceptions.abort(403, "You aren't allowed to modify this member's info.")
    await changing.edit(username=member['username'], rid=member['rid'], fullname=member['name'])
    return sanic.response.raw(b'', status=204)

@member.get('/check-perms')
@uid_get('perms')
@jwtdec.protected()
async def check_perms(rqst, perms):
    def toCamelCase(inp):
        """
        Just so I can access perms idiomatically in TypeScript,
        using camelCase instead of snake_case
        e.g. user.can_check_out in Python, but user.canCheckOut in TS
        """
        return 'can' + ''.join(map(str.capitalize, inp.split('_')))
    perms.namemap = {toCamelCase(k): v for k, v in perms.namemap.items()}
    return sanic.response.json({'perms': perms.props}, status=200)
