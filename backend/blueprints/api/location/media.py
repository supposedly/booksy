"""/api/location/media"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

media = sanic.Blueprint('location_media_api', url_prefix='/media')

@uid_get('location')
@media.get('/search')
@jwtdec.protected()
async def search_location_media(rqst, location):
    try:
        query = rqst.raw_args['query']
    except KeyError:
        sanic.exceptions.abort(422, 'Missing query')
    return await location.search_media(query)

@uid_get('location')
@media.get('/types')
@jwtdec.protected()
async def get_location_media_types(rqst, location):
    return sanic.response.json(await location.media_types())

@uid_get('location', user=True)
@media.post('/types/<action:(add|remove)>')
@jwtdec.protected()
async def edit_location_media_types(rqst, user, location, role, action):
    try:
        type_name = rqst.json['name']
    except KeyError:
        sanic.exceptions.abort(422, 'Missing media type name')
    if not user.perms.can_manage_media:
        sanic.exceptions.abort(401, 'Unauthorized to manage media')
    if action == 'add':
        return sanic.response.json(
          await location.add_media_type(type_name),
          status=200)
    await location.remove_media_type(type_name)
    return sanic.response.raw(status=204)

@uid_get('location') # too many decorators ??? They're all necessary but still...
@rqst_get('data', 'user')
@media.post('/add')
@jwtdec.protected()
async def add_media_item_to_db(rqst, location, data, user):
    if not user.perms.can_manage_items:
        sanic.exceptions.abort(403, 'Unauthorized to manage items.')
    await location.add_media(**data)
    return sanic.response.raw(status=204)

@rqst_get('item', 'user')
@media.post('/remove')
@jwtdec.protected()
async def remove_media_item_from_db(rqst, item, user):
    if not user.perms.can_manage_items:
        sanic.exceptions.abort(403, 'Unauthorized to manage items.')
    await item.remove()
    return sanic.response.raw(status=204)
