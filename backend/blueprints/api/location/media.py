"""/api/location/media"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

media = sanic.Blueprint('location_media_api', url_prefix='/media')

@media.get('/')
@uid_get('location')
@rqst_get('cont')
@jwtdec.protected()
async def search_location_media(rqst, location, cont):
    return sanic.response.json(await location.items(cont=cont), status=200)

@media.get('/search')
@uid_get('location')
@rqst_get('title', 'genre', 'media_type', 'author', 'cont')
@jwtdec.protected()
async def search_location_media(rqst, location, title, genre, media_type, author, cont):
    return sanic.response.json(
      await location.search(
        title = title,
        genre = genre,
        type_ = media_type,
        author = author,
        cont = cont
        ),
      status=200)

@media.get('/types')
@uid_get('location')
@jwtdec.protected()
async def get_location_media_types(rqst, location):
    return sanic.response.json(await location.media_types(), status=200)

@media.post('/types/<action:(add|remove)>')
@uid_get('location', user=True)
@rqst_get('name')
@jwtdec.protected()
async def edit_location_media_types(rqst, user, location, type_name, action):
    if not user.perms.can_manage_media:
        sanic.exceptions.abort(401, 'Unauthorized to manage media.')
    if action == 'add':
        return sanic.response.json(
          await location.add_media_type(type_name),
          status=200)
    await location.remove_media_type(type_name)
    return sanic.response.raw('', status=204)

@media.post('/add')
@uid_get('location')
@rqst_get('data', 'user')
@jwtdec.protected()
async def add_media_item_to_db(rqst, location, data, user):
    if not user.perms.can_manage_items:
        sanic.exceptions.abort(403, 'Unauthorized to manage items.')
    await location.add_media(**data)
    return sanic.response.raw(status=204)

@media.post('/remove')
@rqst_get('item', 'user')
@jwtdec.protected()
async def remove_media_item_from_db(rqst, item, user):
    if not user.perms.can_manage_items:
        sanic.exceptions.abort(403, 'Unauthorized to manage items.')
    await item.remove()
    return sanic.response.raw(status=204)
