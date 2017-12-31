"""/api/media"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

media = sanic.Blueprint('media_api', url_prefix='/media')

@rqst_get('item')
@media.get('/check')
async def get_media_status(rqst, item):
    return sanic.response.json(item.status, status=200)

@rqst_get('user', 'item')
@media.post('/check/out')
@jwtdec.protected()
async def issue_item(rqst, user, item):
    forbidden = user.perms.can_check_out
    if forbidden is not None:
        # `forbidden' will be None if everything's good
        # and a string w/ missing permissions otherwise
        # so if it's nonempty we know someth went wrong
        sanic.exceptions.abort(403, 'Unauthorized to check out.')
    await item.issue_to(user)
    return sanic.response.raw({'checked': 'out', 'title': item.title, 'author': item.author, 'image': item.image_url)

@rqst_get('user', 'item')
@media.post('/check/in')
@jwtdec.protected()
async def return_item(rqst, user, item):
    if not user.perms.can_return_items:
        sanic.exceptions.abort(403, 'Unauthorized to return items.')
    await item.check_in()
    return sanic.response.raw(status=204)

@rqst_get('item')
@media.get('/info')
@jwtdec.protected()
async def get_media_info(rqst, item):
    return sanic.response.json(item.to_dict(), status=200)
