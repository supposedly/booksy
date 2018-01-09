"""/api/media"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

media = sanic.Blueprint('media_api', url_prefix='/media')

@media.post('/hold')
@rqst_get('user', 'title')
@jwtdec.protected()
async def put_item_on_hold(rqst, user, title):
    if user.cannot_check_out:
        sanic.exceptions.abort(403, "You aren't allowed to place holds.")
    if user.holds > user.maxes.holds:
        sanic.exceptions.abort(403, "You aren't allowed to place any more holds.")
    err = await user.hold(title=title)
    if err:
        sanic.exceptions.abort(403, err)
    return sanic.response.raw('', status=204)

@media.get('/check')
@rqst_get('item')
async def get_bool_available(rqst, item):
    return sanic.response.json({'available': item.available, 'issuedTo': item._issued_uid}, status=200)

@media.get('/check/verbose')
@rqst_get('item')
async def get_media_status(rqst, item):
    return sanic.response.json(item.status, status=200)

@media.post('/check/out')
@rqst_get('user', 'item')
@jwtdec.protected()
async def issue_item(rqst, user, item):
    if user.cannot_check_out:
        sanic.exceptions.abort(403, "You aren't allowed to check out.")
    await item.issue_to(user=user)
    return sanic.response.json({'checked': 'out', 'title': item.title, 'author': item.author, 'image': item.image}, status=200)

@media.post('/check/in')
@rqst_get('user', 'item')
@jwtdec.protected()
async def return_item(rqst, user, item):
    if not user.perms.can_return_items:
        sanic.exceptions.abort(403, "You aren't allowed to return items.")
    await item.check_in()
    return sanic.response.raw('', status=204)

@media.get('/info')
@rqst_get('item')
@jwtdec.protected()
async def get_media_info(rqst, item):
    return sanic.response.json(item.to_dict(), status=200)
